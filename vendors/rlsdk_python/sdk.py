# WARNING: core memory manipulation module — interfaces with protected game process
# This module performs direct memory reads/writes and Frida injection
# Unauthorized analysis or redistribution may violate applicable law
import pymem
import pymem.pattern
import ctypes
import frida
import time
import threading
from typing import Callable, Any, Protocol
from .event_handling import Event
from .events import (
    EventFunctionHooked,
    EventBoostPadChanged,
    EventTypes,
    EventPlayerTick,
    EventRoundActiveStateChanged,
    EventResetPickups,
    EventGameEventStarted,
    EventKeyPressed,
    EventGameEventDestroyed,
    EventChatMessage
)
from .game_objects import (
    UClass,
    UFunction,
    GameEvent,
    TArray,
    UObject,
    FNameEntry,
    FName,
    Field,
    VehiclePickupBoost,
    GameViewportClient,
    PlayerController
)
from .frida_script import frida_script
from colorama import Fore, Back, Style, just_fix_windows_console
from tqdm import tqdm
import json
from tabulate import tabulate

PROCESS_NAME = "RocketLeague.exe"

FUNCTION_PICKED_UP = "Function TAGame.VehiclePickup_TA.OnPickUp"
FUNCTION_PLAYER_TICK = "Function TAGame.PlayerController_TA.PlayerTick"
FUNCTION_KEY_PRESS = "Function TAGame.GameViewportClient_TA.HandleKeyPress"
FUNCTION_BALL_CAR_TOUCH = "Function TAGame.Ball_TA.EventCarTouch"
FUNCTION_SET_VEHICLE_INPUT = "Function TAGame.Car_TA.SetVehicleInput"
FUNCTION_PICKUP_TOUCH = "Function TAGame.VehiclePickup_TA.Touch"
FUNCTION_BALL_ON_RIGID_BODY_COLLISION = "Function TAGame.Ball_TA.OnRigidBodyCollision"
FUNCTION_BOOST_PICKED_UP = "Function TAGame.VehiclePickup_Boost_TA.Idle.EndState"
FUNCTION_BOOST_RESPAWN = "Function TAGame.VehiclePickup_Boost_TA.Idle.BeginState"
FUNCTION_ROUND_ACTIVE_BEGIN = "Function TAGame.GameEvent_Soccar_TA.Active.BeginState"
FUNCTION_ROUND_ACTIVE_END = "Function TAGame.GameEvent_Soccar_TA.__GameEvent_Soccar_TA__EndState_0x1"
FUNCTION_RESET_PICKUPS = "Function TAGame.GameEvent_TA.ResetPickups"
FUNCTION_GAMEEVENT_BEGIN_PLAY = "Function TAGame.GameEvent_Soccar_TA.PostBeginPlay"
FUNCTION_GAME_EVENT_ACTIVE_TICK = "Function TAGame.GameEvent_Soccar_TA.Tick"
FUNCTION_GAME_VIEWPORT_CLIENT_TICK = "Function Engine.GameViewportClient.Tick"
FUNCTION_GAME_EVENT_DESTROYED = "Function TAGame.GameEvent_Soccar_TA.Destroyed"
FUNCTION_EVENT_CHAT_MESSAGE = "Function TAGame.GFxData_Chat_TA.OnChatMessage"

CLASS_CORE_OBJECT = "Class Core.Object"

GREEN = "\033[92m"  # Green text
RED = "\033[91m"  # Red text
BLUE = "\033[94m"  # Blue text
YELLOW = "\033[93m"  # Yellow text
END = "\033[0m"  # Reset style

# Event list

ON_FUNCTION_HOOKED = "on_function_called"

class RLSDK:

    def __init__(self, pid=None, hook_player_tick=False, gnames_offset=0x02401648, gobjects_offset=0x02401690):

        self.pid = pid

        try:
            self.pm = pymem.Pymem(self.pid if self.pid else PROCESS_NAME)
            self.frida = frida.attach(self.pid if self.pid else PROCESS_NAME)
        except:
            raise Exception(
                Fore.RED
                + "Rocket League not found. Make sure Rocket League is running."
                + END
            )

        self.g_names_offset = gnames_offset
        self.g_object_offset = gobjects_offset

        self.event = Event()

        self.index_indexed_gnames = {}
        self.gnames = {}

        self.static_classes = {}
        self.static_functions = {}

        self.scan_result = []
        self.scan_response_received_event = threading.Event()

        try:
            self.load_gnames()
            self.map_objects()

            if (
                len(self.gnames) == 0
                or len(self.static_classes) == 0
                or len(self.static_functions) == 0
            ):
                raise Exception("GNames or mapping objects not found")

        except:
            raise Exception(
                Fore.RED
                + "Error while loading GNames and mapping objects. Make sure Rocket League is running."
                + END
            )

        self.process_event_address = self.get_process_event_address()
        self.current_game_event = None

        if self.process_event_address == None:
            print(
                Fore.RED
                + "ProcessEvent address not found. Make sure Rocket League is running."
                + END
            )
            return

        print("ProcessEvent Address: " + hex(self.process_event_address))
        print(
            Fore.GREEN
            + "ProcessEvent address found: "
            + Fore.BLUE
            + hex(self.process_event_address)
            + END
        )

        print(Fore.YELLOW + "Injecting Frida script..." + END)

        self.frida_script = self.frida.create_script(frida_script)
        self.frida_script.load()
        self.frida_script.on("message", self.on_frida_message)

        # send process event address to frida
        self.frida_script.post(
            {"type": "process_event_address", "address": self.process_event_address}
        )

        self.event.subscribe(
            EventTypes.ON_HOOKED_FUNCTION_CALLED, self.on_function_called
        )

        self.hook_function(FUNCTION_BOOST_PICKED_UP)
        self.hook_function(FUNCTION_BOOST_RESPAWN)
        self.hook_function(FUNCTION_ROUND_ACTIVE_BEGIN)
        self.hook_function(FUNCTION_ROUND_ACTIVE_END)
        self.hook_function(FUNCTION_RESET_PICKUPS)
        self.hook_function(FUNCTION_GAMEEVENT_BEGIN_PLAY)
        if hook_player_tick:
            self.hook_function(FUNCTION_PLAYER_TICK, args_map=[("deltatime", "float")])
        self.hook_function(
            FUNCTION_KEY_PRESS, args_map=[( "key_params", "bytes", 0x1C)]
        )
        self.hook_function(FUNCTION_GAME_VIEWPORT_CLIENT_TICK)
        self.hook_function(FUNCTION_GAME_EVENT_DESTROYED)
        self.hook_function(FUNCTION_EVENT_CHAT_MESSAGE, args_map=[
            ("team", "int"),
            ("player_name", "fstring", 0x08),
            ("message", "fstring", 0x18),
            ("chat_channel", "uint8", 0x28)
        ])

        self.field = Field(self)

        time.sleep(1)
        print(Fore.GREEN + "SDK initialized" + END)

    # ==========================================================
    # ================     Offsets finding     =================
    # ==========================================================



    def get_provider(self):
        # Pattern to search for
        pattern = rb"\xBA\xFA\x02\x00\x00\x48\x89\x05"

        # Find the base address of the pattern
        base_address = self.pm.pattern_scan_all(pattern, return_multiple=False)
        if base_address is None:
            return None

        # Calculate the various offsets to reach the final address
        # Read the relative offset from base_address + 8 and add to base_address
        relative_offset = self.pm.read_int(base_address + 8)
        final_address = (
            base_address + 8 + relative_offset + 4
        )  # +4 for the size of the read int

        # Read the UObjectProvider address from the calculated address
        provider_address = self.pm.read_ulonglong(final_address)
        if not provider_address:
            return None

        # The structure starts at provider_address + 0xD8
        tarray_base_address = provider_address + 0xD8

        # Create and return the TArray object
        tarray = TArray(tarray_base_address, UObject, sdk=self)

        return tarray

    def load_gnames(self):

        print(Fore.YELLOW + "Loading GNames..." + END)
        gnames_entries_tarray = self.get_gnames_entries_tarray()
        print(
            Fore.GREEN
            + "GNames count: "
            + Fore.BLUE
            + str(len(gnames_entries_tarray))
            + END
        )

        for gname_entry in tqdm(gnames_entries_tarray):

            if not gname_entry.address:
                continue

            self.gnames[gname_entry.get_index()] = gname_entry.get_name()

        print(Fore.GREEN + "GNames loaded" + END)

    def map_objects(self):
        print(Fore.YELLOW + "Mapping objects..." + END)
        gobjects_tarray = self.get_gobjects_tarray()
        for gobject in tqdm(gobjects_tarray.get_items()):
            try:
                if not gobject.address:
                    continue
                # if full_name content "Class " then it's a UClass

                full_name = gobject.get_full_name()

                if "Class " in full_name:
                    self.static_classes[full_name] = UClass(gobject.address, sdk=self)
                elif "Function " in full_name:
                    self.static_functions[full_name] = UFunction(
                        gobject.address, sdk=self
                    )
            except:
                continue

        print(
            Fore.GREEN + "UClasses: " + Fore.BLUE + str(len(self.static_classes)) + END
        )
        print(
            Fore.GREEN
            + "UFunctions: "
            + Fore.BLUE
            + str(len(self.static_functions))
            + END
        )

    # ==========================================================
    # ================ INTERNAL EVENT HANDLING =================
    # ==========================================================

    def on_function_called(self, event: EventFunctionHooked):

        function_name = event.function.get_full_name()

        if function_name == FUNCTION_BOOST_PICKED_UP:

            pickup = VehiclePickupBoost(int(event.args["caller"], 16), sdk=self)

            boostpad = self.field.find_boostpad_from_pickup(pickup)

            if boostpad:
                boostpad.is_active = False
                boostpad.pickup = pickup
                boostpad.picked_up_time = time.time()

                # update boostpad position to make sure it's accurate (because the pickup is not always at the same position according the map)

                self.field.update_boostpad_from_pickup(boostpad, pickup)

                self.event.fire(
                    EventTypes.ON_BOOSTPAD_CHANGED, EventBoostPadChanged(boostpad)
                )

        elif function_name == FUNCTION_BOOST_RESPAWN:

            pickup = VehiclePickupBoost(int(event.args["caller"], 16), sdk=self)
            boostpad = self.field.find_boostpad_from_pickup(pickup)

            if boostpad:
                boostpad.is_active = True
                boostpad.pickup = pickup
                boostpad.picked_up_time = None

                self.field.update_boostpad_from_pickup(boostpad, pickup)

                self.event.fire(
                    EventTypes.ON_BOOSTPAD_CHANGED, EventBoostPadChanged(boostpad)
                )

        elif function_name == FUNCTION_PLAYER_TICK:

            self.event.fire(
                EventTypes.ON_PLAYER_TICK, EventPlayerTick(event.args["deltatime"])
            )

        elif function_name == FUNCTION_ROUND_ACTIVE_BEGIN:
            self.event.fire(
                EventTypes.ON_ROUND_ACTIVE_STATE_CHANGED,
                EventRoundActiveStateChanged(True),
            )

        elif function_name == FUNCTION_ROUND_ACTIVE_END:
            self.event.fire(
                EventTypes.ON_ROUND_ACTIVE_STATE_CHANGED,
                EventRoundActiveStateChanged(False),
            )

        elif function_name == FUNCTION_RESET_PICKUPS:
            self.event.fire(EventTypes.ON_RESET_PICKUPS, EventResetPickups())
            self.field.reset_boostpads()
        elif function_name == FUNCTION_GAMEEVENT_BEGIN_PLAY:
            self.event.fire(EventTypes.ON_GAME_EVENT_STARTED, EventGameEventStarted())
        elif function_name == FUNCTION_KEY_PRESS:
            params = event.args["key_params"]

            data_bytes = bytes.fromhex(params)
            fname_entry_id = int.from_bytes(data_bytes[4:8], byteorder="little")
            key_name = self.gnames[fname_entry_id]
            ev = EventKeyPressed(data_bytes, key_name)

            self.event.fire(EventTypes.ON_KEY_PRESSED, ev)

        elif function_name == FUNCTION_GAME_VIEWPORT_CLIENT_TICK:
            viewport = GameViewportClient(int(event.args["caller"], 16), sdk=self)
            self.current_game_event = viewport.get_game_event()

        elif function_name == FUNCTION_GAME_EVENT_DESTROYED:
            self.current_game_event = None
            self.event.fire(
                EventTypes.ON_GAME_EVENT_DESTROYED, EventGameEventDestroyed()
            )

        elif function_name == FUNCTION_EVENT_CHAT_MESSAGE:
            print("Chat message received")
            print(event.args)
            
            # player_controller = PlayerController(
            #     int(event.args["player_controller"], 16), sdk=self
            # )
            # message = event.args["message"]
            # preset = event.args["preset"]   

            # self.event.fire(
            #     EventTypes.ON_CHAT_MESSAGE,
            #     EventChatMessage(player_controller, message, preset)
            # )
            

    # ==========================================================
    # ===================== DEBUG METHODS ======================
    # ==========================================================


    def scan_functions(self, duration=10):
        print("Scanning functions...")
        self.scan_response_received_event.clear()
        self.frida_script.post({"type": "scan_functions", "duration": duration})
        received = self.scan_response_received_event.wait(duration + 10)
        if received:
            
            print("Scan result received.")

            headers = ["Count", "Address", "ThreadId", "Function Name"]
            table = []
            for func in self.scan_result:
                count = Fore.GREEN + str(func.get("count")) + Style.RESET_ALL
                address = Fore.BLUE + func.get("address") + Style.RESET_ALL
                thread_id = Fore.YELLOW + str(func.get("thread_id")) + Style.RESET_ALL
                name = Fore.MAGENTA + func.get("name") + Style.RESET_ALL
                table.append([count, address, thread_id, name])

            print(tabulate(table, headers, tablefmt="fancy_grid"))
            print("Unique functions scanned: " + str(len(self.scan_result)))
            return self.scan_result
        else:
            print("Scan timed out.")
            return None

    # ==========================================================
    # ================ EXTRACTION METHODS ======================
    # ==========================================================

    def extract_classes(self):
        # write all classes name to a file with their address
        print("Extracting classes...")
        filename = "classes.txt"
        with open(filename, "w") as file:
            for class_name, class_object in self.static_classes.items():
                file.write(hex(class_object.address) + " : " + class_name + "\n")
        print("Classes extracted to " + filename)

    def extract_functions(self):
        # write all functions name to a file with their address
        print("Extracting functions...")
        filename = "functions.txt"
        with open(filename, "w") as file:
            for function_name, function_object in self.static_functions.items():
                file.write(hex(function_object.address) + " : " + function_name + "\n")
        print("Functions extracted to " + filename)

    # ==========================================================
    # ================ FRIDA HOOKING METHODS ===================
    # ==========================================================

    def on_frida_message(self, message, data):

        if message["type"] == "send":
            payload = message["payload"]
            if payload.get("type") == "hooked_function_fired":
                function = UFunction(int(payload.get("address"), 16), sdk=self)

                self.event.fire(
                    EventTypes.ON_HOOKED_FUNCTION_CALLED,
                    EventFunctionHooked(function, payload.get("args")),
                )

            if payload.get("type") == "scan_result":
                for f in payload.get("functions"):
                    ufunction = UFunction(int(f.get("address"), 16), sdk=self)
                    self.scan_result.append({
                        "address": f.get("address"),
                        "object": ufunction,
                        "name": ufunction.get_full_name(),
                        "count": f.get("count"),
                        "thread_id": f.get("thread_id")
                    })
                    
                self.scan_response_received_event.set()
            elif payload.get("type") == "log":
                print(Fore.MAGENTA + "Frida log: " + END + payload.get("message"))

        else:
            print("Received message:", message)

    def hook_function(self, function_name, args_map=[]):

        function_address = self.find_static_function(function_name).address
        if function_address:
            self.frida_script.post(
                {
                    "type": "hook_function",
                    "address": function_address,
                    "name": function_name,
                    "args_map": args_map,
                }
            )
        else:
            pass

    def get_process_event_address(self):
        core_object = self.find_static_class(CLASS_CORE_OBJECT)
        if core_object:
            print("Core Object Address: " + hex(core_object.address))
            vtable_address = self.pm.read_ulonglong(core_object.address)
            return self.pm.read_ulonglong(vtable_address + (0x8 * 67))
        return None

    # ==========================================================
    # ===================== Accessors ==========================
    # ==========================================================

    def get_game_event(self):
        return self.current_game_event

    def get_field(self):
        return self.field

    def get_gobjects_tarray(self):
        return TArray(
            self.pm.base_address + self.g_object_offset, UObject, sdk=self
        )  # Replace UObject with the appropriate class

    def get_gnames_entries_tarray(self):
        return TArray(self.pm.base_address + self.g_names_offset, FNameEntry, sdk=self)

    def get_pm(self):
        return self.pm

    # ==========================================================
    # =====================   Methods  =========================
    # ==========================================================

    def get_name(self, index):
        return self.gnames.get(index)

    def find_static_function(self, function_name):
        return self.static_functions.get(function_name)

    def find_static_class(self, class_name):
        return self.static_classes.get(class_name)

    # Use to read cheat engine pointer offsets if needed
    def get_offsets_final_address(self, offsets):
        if self.pm != None:
            base_address = self.pm.base_address
            for offset in offsets:
                base_address = self.pm.read_ulonglong(base_address + offset)
            return base_address

    def create_callable_function(self, function_name, arg_types=None):
        TYPE_SIZES = {
            "float": 4,
            "int": 4,
            "uint": 4,
            "uint32": 4,
            "uint8": 1,
            "pointer": 8,  # 64 bits
            "bool": 1,  # Boolean for flags, often used as uint8_t
            "fstring": 16,  # FString is a 16-byte structure
        }
        function = self.find_static_function(function_name)
        if function:

            def call_function(caller: UObject, **kwargs):
                args = []
                total_size = 0
                if arg_types:
                    # Prepare the arguments for Frida
                    for arg_name, arg_type in arg_types.items():

                        if arg_type == "pointer":
                            if isinstance(kwargs.get(arg_name), UObject):
                                value = kwargs.get(arg_name).address
                                size = TYPE_SIZES[arg_type]
                            else:
                                raise Exception("Argument must be a UObject instance")
                        elif arg_type == "string":

                            # check if the string is a string
                            if isinstance(kwargs.get(arg_name), str):
                                value = kwargs.get(arg_name)
                                size = len(kwargs.get(arg_name)) + 1
                            else:
                                raise Exception("Argument must be a string")
                        else:
                            value = kwargs.get(arg_name)
                            size = TYPE_SIZES[arg_type]
                        total_size += size
                        args.append(
                            {
                                "name": arg_name,
                                "type": arg_type,
                                "value": value,
                                "size": size,
                            }
                        )

                self.frida_script.post(
                    {
                        "type": "call_function",
                        "function_address": function.address,
                        "caller_address": caller.address,
                        "args": args,
                        "total_size": total_size,
                    }
                )

            return call_function
        else:
            raise Exception("Function not found")
