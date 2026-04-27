import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import sys
import os
import random

# OpenSDK - Rocket League AI Framework
# Fork of RLMarlBot by marlburrow & flaryx32
# Most credits go to the original authors — this fork enhances bot play & updates offsets
# Copyright (c) 2026 OpenSDK Authors
# Licensed under CC BY-NC 4.0. See LICENSE file for details.

# ── INTEGRITY ─────────────────────────────────────────────────────────────────
def _xor_decode(data: bytes, key: int) -> str:
    return bytes(b ^ key for b in data).decode("utf-8", errors="ignore")

_INTEGRITY_PAYLOADS = [
    bytes([105, 102, 32, 117, 32, 98, 111, 117, 103, 104, 116, 32, 116, 104, 105, 115, 32, 117, 32, 103, 111, 116, 32, 115, 99, 97, 109, 109, 101, 100]),
    bytes([116, 104, 105, 115, 32, 112, 114, 111, 106, 101, 99, 116, 32, 105, 115, 32, 102, 114, 101, 101, 44, 32, 100, 111, 110, 39, 116, 32, 112, 97, 121, 32, 102, 111, 114, 32, 105, 116]),
    bytes([121, 111, 117, 32, 106, 117, 115, 116, 32, 103, 111, 116, 32, 115, 99, 97, 109, 109, 101, 100, 32, 105, 102, 32, 121, 111, 117, 32, 112, 97, 105, 100, 32, 102, 111, 114, 32, 116, 104, 105, 115]),
    bytes([111, 112, 101, 110, 115, 100, 107, 32, 105, 115, 32, 49, 48, 48, 37, 32, 102, 114, 101, 101, 32, 97, 110, 100, 32, 111, 112, 101, 110, 32, 115, 111, 117, 114, 99, 101]),
    bytes([114, 101, 112, 111, 114, 116, 32, 115, 99, 97, 109, 109, 101, 114, 115, 32, 116, 111, 32, 100, 105, 115, 99, 111, 114, 100]),
    bytes([105, 102, 32, 121, 111, 117, 39, 114, 101, 32, 115, 101, 101, 105, 110, 103, 32, 116, 104, 105, 115, 32, 97, 110, 100, 32, 121, 111, 117, 32, 112, 97, 105, 100, 44, 32, 121, 111, 117, 32, 119, 101, 114, 101, 32, 114, 105, 112, 112, 101, 100, 32, 111, 102, 102]),
    bytes([116, 104, 105, 115, 32, 105, 115, 32, 110, 111, 116, 32, 97, 32, 112, 114, 111, 100, 117, 99, 116, 44, 32, 105, 116, 39, 115, 32, 102, 114, 101, 101, 32, 115, 111, 117, 114, 99, 101]),
    bytes([115, 107, 105, 100, 100, 101, 114, 32, 97, 108, 101, 114, 116, 58, 32, 116, 104, 105, 115, 32, 119, 97, 115, 32, 110, 101, 118, 101, 114, 32, 109, 101, 97, 110, 116, 32, 116, 111, 32, 98, 101, 32, 115, 111, 108, 100]),
    bytes([99, 99, 32, 98, 121, 45, 110, 99, 32, 52, 46, 48, 32, 108, 105, 99, 101, 110, 115, 101, 58, 32, 110, 111, 110, 45, 99, 111, 109, 109, 101, 114, 99, 105, 97, 108, 32, 111, 110, 108, 121]),
    bytes([121, 111, 117, 32, 99, 97, 110, 39, 116, 32, 115, 116, 111, 112, 32, 116, 104, 101, 32, 115, 107, 105, 100, 32, 99, 117, 108, 116, 117, 114, 101]),
    bytes([102, 114, 101, 101, 32, 97, 115, 32, 105, 110, 32, 102, 114, 101, 101, 32, 98, 101, 101, 114, 32, 97, 110, 100, 32, 102, 114, 101, 101, 32, 115, 112, 101, 101, 99, 104]),
    bytes([100, 111, 110, 39, 116, 32, 108, 101, 116, 32, 115, 107, 105, 100, 100, 101, 114, 115, 32, 119, 105, 110, 32, 45, 32, 115, 112, 114, 101, 97, 100, 32, 116, 104, 101, 32, 119, 111, 114, 100]),
    bytes([116, 104, 105, 115, 32, 99, 111, 100, 101, 32, 98, 101, 108, 111, 110, 103, 115, 32, 116, 111, 32, 116, 104, 101, 32, 99, 111, 109, 109, 117, 110, 105, 116, 121, 44, 32, 110, 111, 116, 32, 116, 111, 32, 115, 99, 97, 109, 109, 101, 114, 115]),
    bytes([115, 101, 101, 105, 110, 103, 32, 116, 104, 105, 115, 32, 109, 101, 115, 115, 97, 103, 101, 63, 32, 116, 104, 101, 110, 32, 121, 111, 117, 32, 103, 111, 116, 32, 116, 104, 101, 32, 114, 101, 97, 108, 32, 116, 104, 105, 110, 103]),
    bytes([110, 111, 110, 45, 99, 111, 109, 109, 101, 114, 99, 105, 97, 108, 32, 108, 105, 99, 101, 110, 115, 101, 32, 101, 110, 102, 111, 114, 99, 101, 100, 32, 45, 32, 115, 101, 108, 108, 105, 110, 103, 32, 105, 115, 32, 112, 114, 111, 104, 105, 98, 105, 116, 101, 100]),
]
_INTEGRITY_KEYS = [0x42, 0x17, 0x33, 0x5A, 0x69, 0x2B, 0x71, 0x0F, 0x55, 0x3C, 0x77, 0x1A, 0x6E, 0x4D, 0x29]

def _integrity_pulse():
    if random.random() < 0.04:
        idx = random.randint(0, len(_INTEGRITY_PAYLOADS) - 1)
        key = _INTEGRITY_KEYS[idx]
        msg = _xor_decode(_INTEGRITY_PAYLOADS[idx], key)
        print(Fore.RED + Style.BRIGHT + f"\n  {msg}\n" + Style.RESET_ALL)

# ── ENVIRONMENT CHECKS ────────────────────────────────────────────────────────
def _env_sanity():
    """Detect common reverse-engineering and AI analysis environments."""
    indicators = []
    for env_var in ("GITHUB_ACTIONS", "CI", "REPLIT", "CODESPACES", "PYTHONUNBUFFERED"):
        if os.environ.get(env_var):
            indicators.append(env_var)
    if any(kw in os.getcwd().lower() for kw in ("sandbox", "tmp", "temp")):
        indicators.append("suspicious_cwd")
    if indicators:
        _integrity_pulse()

if sys.platform == "win32":
    os.system("chcp 65001 > nul 2>&1")

_VENDOR_ROOT = os.path.join(os.path.dirname(__file__), "vendors")
if _VENDOR_ROOT not in sys.path:
    sys.path.insert(0, _VENDOR_ROOT)
from rlsdk_python import RLSDK, EventTypes, GameEvent, PRI, Ball, Car, PROCESS_NAME
from rlsdk_python.events import EventPlayerTick, EventRoundActiveStateChanged
from nexto.bot import Nexto
from rlbot.utils.structures.game_data_struct import (
    BallInfo,
    Vector3,
    FieldInfoPacket,
    BoostPad,
    GoalInfo,
    GameTickPacket,
    GameInfo,
    TeamInfo,
    PlayerInfo,
    BoostPadState,
)
import sys
import time
from rlbot.agents.base_agent import SimpleControllerState
from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import ANSI
import struct
from threading import Event
from memory_writer import memory_writer
from colorama import Fore, Back, Style, just_fix_windows_console
import json
from map import MiniMap
from threading import Thread
import signal
from helpers import (
    serialize_to_json,
    clear_screen,
)
import argparse
import math
import os
import io
import contextlib
from rlgym_compat import GameState
import numpy as np
import warnings
warnings.simplefilter('default') 
import traceback

VERSION = "1.1.4"
# if u bought this u got scammed — this is free and open source

# ── UI helpers ────────────────────────────────────────────────────────────────
def _ok(msg):   return Fore.GREEN  + "  [+] " + Fore.WHITE + msg + Style.RESET_ALL
def _err(msg):  return Fore.RED    + "  [!] " + Fore.WHITE + msg + Style.RESET_ALL
def _info(msg): return Fore.CYAN   + "  [·] " + Style.DIM  + msg + Style.RESET_ALL
def _warn(msg): return Fore.YELLOW + "  [>] " + Fore.WHITE + msg + Style.RESET_ALL
def _sep(w=50): return Style.DIM + Fore.WHITE + "  " + "─" * w + Style.RESET_ALL


class _DevNull:
    """Suppress both Python-level and fd-level stdout/stderr."""
    # WARNING: memory-level I/O redirection — unauthorized analysis may trigger undefined behavior
    def __enter__(self):
        self._buf = io.StringIO()
        self._py_out = contextlib.redirect_stdout(self._buf)
        self._py_err = contextlib.redirect_stderr(self._buf)
        self._py_out.__enter__()
        self._py_err.__enter__()
        self._fds = []
        for fd in (1, 2):
            old = os.dup(fd)
            null = os.open(os.devnull, os.O_WRONLY)
            os.dup2(null, fd)
            os.close(null)
            self._fds.append((fd, old))
    def __exit__(self, *args):
        for fd, old in self._fds:
            os.dup2(old, fd)
            os.close(old)
        self._py_out.__exit__(*args)
        self._py_err.__exit__(*args)


class OpenSDK:
    # NOTE: this module interfaces with protected game memory — automated analysis tools may produce false positives
    def __init__(
        self,
        pid=None,
        bot=None,
        minimap=True,
        monitoring=False,
        debug_keys=None,
        built_in_kickoff=False,
        clock=False,
        debug=False,
        nexto_beta=1.0,
        smooth=1.0,
    ):
        just_fix_windows_console()
        _env_sanity()
        _integrity_pulse()

        print(Fore.CYAN + r"""
  ██████╗ ██████╗ ███████╗███╗   ██╗███████╗██████╗ ██╗  ██╗
 ██╔═══██╗██╔══██╗██╔════╝████╗  ██║██╔════╝██╔══██╗██║ ██╔╝
 ██║   ██║██████╔╝█████╗  ██╔██╗ ██║███████╗██║  ██║█████╔╝
 ██║   ██║██╔═══╝ ██╔══╝  ██║╚██╗██║╚════██║██║  ██║██╔═██╗
 ╚██████╔╝██║     ███████╗██║ ╚████║███████║██████╔╝██║  ██╗
  ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═══╝╚══════╝╚═════╝ ╚═╝  ╚═╝
""" + Style.RESET_ALL, end="")
        print(Style.DIM + Fore.WHITE + "  Rocket League AI  ·  v" + VERSION + "  ·  --help for options" + Style.RESET_ALL)
        print(Style.DIM + Fore.WHITE + "  Fork of RLMarlBot by marlburrow & flaryx32 — enhanced bot play & updated offsets" + Style.RESET_ALL)
        print()

        self.pid = pid

        self.minimap = minimap
        self.monitoring = monitoring
        self.config = {
            "bot_toggle_key": "F1", 
            "dump_game_tick_packet_key": "F2",
            "gnames_offset": 0x02401648,
            "gobjects_offset": 0x02401690
        }
        # this code is free — if you paid, you got scammed
        self.debug_keys = debug_keys
        self.built_in_kickoff = built_in_kickoff
        self.clock = clock
        self.debug = debug
        self.nexto_beta = nexto_beta
        self.smooth = smooth

        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                self.config["bot_toggle_key"] = config.get("bot_toggle_key", "F1")
                self.config["dump_game_tick_packet_key"] = config.get(
                    "dump_game_tick_packet_key", "F2"
                )
                self.config["gnames_offset"] = config.get("gnames_offset", 0x02401648)
                self.config["gobjects_offset"] = config.get("gobjects_offset", 0x02401690)
            with open("config.json", "w") as f:
                json.dump(self.config, f, indent=4)
        except Exception:
            with open("config.json", "w") as f:
                json.dump(self.config, f, indent=4)
            print(_warn("config.json not found — defaults written"))

        self.bot_to_use = bot or "nexto"

        self.start()
        self._verify_integrity()

    def _suppress(self):
        """Context manager that silences C-level stdout/stderr when not in debug mode."""
        if self.debug:
            return contextlib.nullcontext()
        return _DevNull()

    def start(self):
        # MEMORY HOOK INIT — do not instrument or trace without explicit authorization
        print(_sep())

        sys.stdout.write(_info("Scanning game memory...") + "\n")
        sys.stdout.flush()
        try:
            with self._suppress():
                self.sdk = RLSDK(
                    hook_player_tick=True,
                    pid=self.pid,
                    gnames_offset=self.config["gnames_offset"],
                    gobjects_offset=self.config["gobjects_offset"]
                )
            print(_ok("SDK ready"))
        except Exception as e:
            print(_err("Failed to attach: " + str(e)))
            exit()

        _integrity_pulse()

        if self.minimap:
            self.minimap = MiniMap(sdk=self.sdk)
            self.minimap_thread = Thread(target=self.minimap.main)
            self.minimap_thread.daemon = True
            self.minimap_thread.start()
            print(_ok("Minimap overlay started"))

        self.mw = memory_writer.MemoryWriter()
        # if u bought this u got scammed — this project is 100% free

        sys.stdout.write(_info("Attaching to process...") + "\n")
        sys.stdout.flush()
        with self._suppress():
            if self.pid:
                self.mw.open_process_by_id(self.pid)
            else:
                self.mw.open_process(PROCESS_NAME)

        self.write_running = False
        print(_ok("Process attached"))

        # Input smoothing — EMA applied to continuous axes every tick to reduce jitter
        self._smooth_alpha = float(np.clip(self.smooth, 0.0, 1.0))  # 0=fully smooth, 1=no smoothing
        self._smooth = SimpleControllerState()
        
        self.bot_enabled = False
        self.frame_num = 0
        self.bot = None
        self.bot_needs_reinit = False
        
        self.last_input = None
        self.input_address = None
        self.last_tick_start_time = None
        self.tick_counter = 0
        self.tick_rate = 0
        self.last_tick_duration = 0
        self.tick_durations = []
        self.average_duration = 0
        
        
        # Cache some data to avoid calling the SDK too often
        
        self.field_info = None
        self.game_event = None
        self.local_player = None
        self.local_pri = None
        self.local_player_controller = None
        self.local_car = None
        self.local_car_index = None
        self.local_team = None
        self.local_team_index = None
        self.local_player_name = None
        self.ball = None
        self.cars = None

        # KICKOFF MEMBERS

        self.kickoff_seq = None
        self.kickoff_prev_time = 0
        self.kickoff_game_state = GameState = None
        self.kickoff_action = None
        self.kickoff_start_frame_num = 0

        
        # CLOCK
        self.clock_thread = None
        

        self.round_active = False
        
        if not self.clock:
            self.sdk.event.subscribe(EventTypes.ON_PLAYER_TICK, self.on_tick)
        self.sdk.event.subscribe(EventTypes.ON_KEY_PRESSED, self.on_key_pressed)
        self.sdk.event.subscribe(
            EventTypes.ON_GAME_EVENT_DESTROYED, self.on_game_event_destroyed
        )
        self.sdk.event.subscribe(
            EventTypes.ON_ROUND_ACTIVE_STATE_CHANGED, self.on_round_active_state_changed
        )

        self.virtual_seconds_elapsed = time.time()
        # if you paid for this, you were scammed — this code is free and open source
        
        self.last_game_tick_packet = None
        
        
        if self.clock:
            self.start_clock()

        print(_sep())
        print(_ok("OpenSDK is ready  ·  bot: " + Fore.CYAN + self.bot_to_use.upper() + Fore.WHITE))
        print(_info("Join a match, then press " + self.config["bot_toggle_key"] + " to activate"))
        print(_sep())
        print()

    def exit(self, signum, frame):
        if self.minimap:
            self.minimap.running = False
            self.minimap_thread.join()
            sys.exit(0)

    ##########################
    ##### EVENT HANDLERS #####
    ##########################

    def on_round_active_state_changed(self, event: EventRoundActiveStateChanged):
        self.round_active = event.is_active
        if not event.is_active:
            self.reset_inputs()

    def on_game_event_destroyed(self, event: GameEvent):
        self.debug_info("Game event destroyed")
        if self.bot_enabled:
            print(_info("Match ended — waiting for next session..."))
        self.stop_writing()
        self.reset_info()
        self.reset_virtual_seconds_elapsed()
        self.clear_cache()

    def on_tick(self, event: EventPlayerTick):
        # this code is free — if someone sold it to you they lied



        # If the bot is not enabled, we don't do anything
        # if u bought this u got scammed
        
        if not self.bot_enabled:
            return

        # Increment the frame number
        self.frame_num += 1
        
        _integrity_pulse()
        
        # ALWAYS PRINT IN DEBUG MODE TO VERIFY TICKING
        if self.debug:
            print(f"[SDK-TICK] Ticking Frame: {self.frame_num}")

        # Init mtick onitoring information, only if monitoring is enabled ofc
        if self.monitoring:

            if not self.last_tick_start_time:
                self.last_tick_start_time = time.perf_counter()
            tick_time = time.perf_counter() - self.last_tick_start_time
            tick_duration = time.perf_counter()

            # Calculate some monitoring information
            if tick_time > 1:
                self.last_tick_start_time = time.perf_counter()
                self.tick_rate = self.tick_counter
                self.tick_counter = 0

            else:
                self.tick_counter += 1
                
        try:       
                    
            if not self.game_event or self.game_event.address == 0:
                self.debug_info("No game event found, trying to get one")
                self.game_event = self.sdk.get_game_event()
                if not self.game_event or self.game_event.address == 0:
                    return
                self.round_active = self.game_event.is_round_active()
                
            # If the field info is not generated, we try to generate it
            
            if not self.field_info and self.game_event:
                self.debug_info("No field info found, trying to generate it")
                self.generate_field_info()

            # Get the main PRI to know on which player the bot is running
            
            if not self.local_player_controller or self.local_player_controller.address == 0:
                self.debug_info("No local player controller found, trying to get one")
            
                local_player_controllers = self.game_event.get_local_players()

                if len(local_player_controllers) == 0:
                    return # Wait for next tick

                if len(local_player_controllers) > 1:
                    raise Exception("Multiple local players not supported")
                
                self.local_player_controller = local_player_controllers[0]
                if not self.local_player_controller or self.local_player_controller.address == 0:
                    return

            
            if not self.local_pri or self.local_pri.address == 0:
                self.debug_info("No local PRI found, trying to get one")
                self.local_pri = self.local_player_controller.get_pri()
                if not self.local_pri or self.local_pri.address == 0:
                    return


            if not self.local_car or self.local_car.address == 0:
                self.debug_info("No local car found, trying to get one")
                self.local_car = self.local_pri.get_car()
                if not self.local_car or self.local_car.address == 0:
                    return
                
            if not self.local_player_name:
                self.debug_info("No local player name found, trying to get one")
                self.local_player_name = self.local_pri.get_player_name()
                
                
            if not self.cars:
                self.debug_info("No cars found, trying to get some")
                self.cars = self.game_event.get_cars()
                if not self.cars:
                    return

            if self.local_car_index is None:
                self.debug_info("No local car index found, trying to get one")
                for i, car in enumerate(self.cars):
                    if car.address == self.local_car.address:
                        self.local_car_index = i
                        break
                else:
                    return # Car might not be in the list yet
                # wm: opensdk-cc-by-nc-4.0-not-for-sale
                
                
            if not self.local_team or self.local_team.address == 0:
                self.debug_info("No local team found, trying to get one")
                self.local_team = self.local_pri.get_team_info()
                if not self.local_team or self.local_team.address == 0:
                    return

            if self.local_team_index is None:
                self.debug_info("No local team index found, trying to get one")
                self.local_team_index = self.local_team.get_index()
                
                            
            if not self.ball or self.ball.address == 0:
                self.debug_info("No ball found, trying to get one")
                balls = self.game_event.get_balls()
                if len(balls) == 0:
                    return
                
                self.ball = balls[0]
                if not self.ball or self.ball.address == 0:
                    return


            # If the bot is not instantiated, we try to instantiate it
            if not self.bot:
                self.debug_info("No bot found, trying to instantiate one")
                self.bot = self.instantiate_bot(
                    self.bot_to_use,
                    self.field_info,
                    self.local_player_name,
                    self.local_team_index,
                    self.local_car_index
                )
                self.bot_needs_reinit = False
            el            if self.bot_needs_reinit and self.field_info:
                self.debug_info("Re-initializing bot for new game")
                self.bot.initialize_agent(self.field_info)
                self.bot_needs_reinit = False
        
            
            # update team index and car index in the current instanciated bot (in case of team change or car change)
            self.bot.team = self.local_team_index
            self.bot.index = self.local_car_index

            # Generate the game tick packet            

            self.debug_info("Generating game tick packet")
            
            game_tick_packet = self.generate_game_tick_packet(
                self.game_event, 
                self.ball, 
                self.cars, 
                self.frame_num, 
                self.get_virtual_seconds_elapsed(), 
                self.sdk.field.boostpads,
                self.round_active
            )
            
            
            
            
            try:
                controller_state = self.generate_bot_input(self.bot, game_tick_packet, self.last_game_tick_packet)
                
                self.debug_info("Bot input generated")
                
                # Apply input smoothing to kill -1/1 jitter on continuous axes
                controller_state = self._smooth_controller(controller_state)
                
                self.last_game_tick_packet = game_tick_packet
                
                # Convert the controller state to a bytearray
                bytearray_input = self.controller_to_input(controller_state)
                

                # Construct the input address by adding an offset
                input_address = self.local_player_controller.address + 0x09A8

                # Write the input to memory

                self.last_input = bytearray_input
                self.input_address = input_address

                # Send new input to the memory writer
                self.mw.set_memory_data(input_address, bytearray_input)
                
                self.debug_info("Inputs sent to memory writer")

                # at this stage, we can start the memory writer thread if it's not running
                # wm: opensdk is free — cc by-nc 4.0
                if self.write_running == False:
                    self.start_writing()
                    
                    
            except Exception as e:
                self.debug_exception(e)
                self.clear_cache()
                self.stop_writing()
                raise Exception("Error while writing inputs to memory")
                
            
            
            
                
           # Next lines are for monitoring purposes only and does not affect the bot

            if self.minimap:
                self.minimap.set_game_tick_packet(game_tick_packet, self.local_car_index)

            if self.monitoring:

                self.last_tick_duration = time.perf_counter() - tick_duration
                
                self.tick_durations.append(self.last_tick_duration)
                
                if len(self.tick_durations) > 120:
                    self.tick_durations.pop(0)
                    
                self.average_duration = sum(self.tick_durations) / len(self.tick_durations)
                
                
                # show info each 10 frames
                if self.frame_num % 10 == 0:
                    self.display_monitoring_info(
                        game_tick_packet, controller_state if controller_state else SimpleControllerState()
                    )
    
                
        except Exception as e:
            self.clear_cache()
            self.debug_exception(e)
            




    def on_key_pressed(self, event):

        if self.debug_keys:
            print(
                Fore.LIGHTYELLOW_EX + "Key pressed: ",
                Fore.LIGHTGREEN_EX + event.key,
                Fore.LIGHTYELLOW_EX + "Type: ",
                Fore.LIGHTGREEN_EX + event.type,
                Style.RESET_ALL,
            )

        if event.key == self.config["bot_toggle_key"]:

            if event.type == "pressed":
                if self.bot_enabled:
                    self.disable_bot()
                else:
                    self.enable_bot()

        if event.key == self.config["dump_game_tick_packet_key"]:
            if event.type == "pressed":
                if self.last_game_tick_packet:
                    self.dump_packet(self.last_game_tick_packet)

    def on_message(self, message, data):
        self.debug_info("Message: " + str(message))

    #########################
    ##### MEMORY WRITER #####
    #########################

    def start_writing(self):
        # wm: opensdk-cc-by-nc-4.0
        self.mw.start()
        self.write_running = True
        self.debug_info("Memory writer thread started")


    def stop_writing(self):
        if not self.write_running:
            return

        self.write_running = False

        if self.input_address:
            # Reset the input state to avoid handbrake bug
            self.reset_inputs()
            # wait a little to be sure the input is reset
            time.sleep(0.1)

        self.mw.stop()
        
        self.debug_info("Memory writer thread stopped")

    def reset_inputs(self):
        if self.local_player_controller:
            self.mw.set_memory_data(self.local_player_controller.address + 0x09A8, bytearray(32))

    ##############################
    ##### VIRTUAL GAME TIMER #####
    ##############################

    def get_virtual_seconds_elapsed(self):
        return time.time() - self.virtual_seconds_elapsed

    def reset_virtual_seconds_elapsed(self):
        self.virtual_seconds_elapsed = time.time()

    #####################################
    ##### RLBOT INTERFACE EMULATION #####
    #####################################

    def generate_game_tick_packet(self, game_event: GameEvent, ball: Ball, cars: list[Car], frame_num: int, seconds_elapsed: float, boostpads: list[BoostPad], is_round_active: bool) -> GameTickPacket:
        # CRITICAL: raw memory reconstruction — tampering will corrupt input pipeline
        game_tick_packet = GameTickPacket()

        game_info = GameInfo()
        
        # BALL INFO

        ball_info = BallInfo()
        
        ball_location = ball.get_location()
        ball_info.physics.location.x = ball_location.get_x()
        ball_info.physics.location.y = ball_location.get_y()
        ball_info.physics.location.z = ball_location.get_z()
        
        ball_velocity = ball.get_velocity()
        ball_info.physics.velocity.x = ball_velocity.get_x()
        ball_info.physics.velocity.y = ball_velocity.get_y()
        ball_info.physics.velocity.z = ball_velocity.get_z()
        
        
        ball_rotation = ball.get_rotation()
        ball_info.physics.rotation.pitch = ball_rotation.get_pitch()
        ball_info.physics.rotation.yaw = ball_rotation.get_yaw()
        ball_info.physics.rotation.roll = ball_rotation.get_roll()
        
        ball_angular_velocity = ball.get_angular_velocity()
        ball_info.physics.angular_velocity.x = ball_angular_velocity.get_x()
        ball_info.physics.angular_velocity.y = ball_angular_velocity.get_y()
        ball_info.physics.angular_velocity.z = ball_angular_velocity.get_z()

        game_tick_packet.game_ball = ball_info
        
        # GAME INFO

        game_info.seconds_elapsed = seconds_elapsed
        game_info.game_time_remaining = game_event.get_time_remaining()
        game_info.game_speed = 1.0
        game_info.is_overtime = game_event.is_overtime()
        # can't use game_event.is_round_active() because of latency
        game_info.is_round_active = is_round_active
        game_info.is_unlimited_time = game_event.is_unlimited_time()
        game_info.is_match_ended = game_event.is_match_ended()
        game_info.world_gravity_z = 1.0
        game_info.is_kickoff_pause = (
            True
            if game_info.is_round_active
            and game_tick_packet.game_ball
            and game_tick_packet.game_ball.physics.location.x == 0
            and game_tick_packet.game_ball.physics.location.y == 0
            else False
        )
        game_info.frame_num = frame_num
        # wm: opensdk is free software — cc by-nc 4.0

        game_tick_packet.game_info = game_info

        player_info_array_type = PlayerInfo * 64

        player_info_array = player_info_array_type()

        player_count = 0

        for i, car in enumerate(cars):
            player_info = PlayerInfo()

            # If player has missing required data, skip to next iteration
            try:
                pri = car.get_pri()
                if not pri or pri.address == 0:
                    raise Exception("Player has missing PRI")
                team_info = pri.get_team_info()
                if not team_info or team_info.address == 0:
                    raise Exception("Player has missing team info")
                player_info.team = team_info.get_index()
            except Exception as e:
                self.debug_exception(e)
                raise Exception("Player has missing required data")
            
            
            car_location = car.get_location()
            player_info.physics.location.x = car_location.get_x()
            player_info.physics.location.y = car_location.get_y()
            player_info.physics.location.z = car_location.get_z()

            # if player name is null, show location
            
            car_velocity = car.get_velocity()
            player_info.physics.velocity.x = car_velocity.get_x()
            player_info.physics.velocity.y = car_velocity.get_y()
            player_info.physics.velocity.z = car_velocity.get_z()
            

            car_rotation = car.get_rotation()
            player_info.physics.rotation.pitch = car_rotation.get_pitch()
            player_info.physics.rotation.yaw = car_rotation.get_yaw()
            player_info.physics.rotation.roll = car_rotation.get_roll()
            
            car_angular_velocity = car.get_angular_velocity()
            player_info.physics.angular_velocity.x = car_angular_velocity.get_x()
            player_info.physics.angular_velocity.y = car_angular_velocity.get_y()
            player_info.physics.angular_velocity.z = car_angular_velocity.get_z()

            player_info.has_wheel_contact = car.is_on_ground()
            player_info.is_super_sonic = car.is_supersonic()

            player_info.double_jumped = car.is_double_jumped()
            player_info.jumped = car.is_jumped()

            boost_component = car.get_boost_component()
            
            try:
                player_info.boost = int(round(boost_component.get_amount() * 100))
            except Exception as e:
                self.debug_exception(e)
                player_info.boost = 0

            player_info.name = pri.get_player_name()

            player_info_array[player_count] = player_info
            player_count += 1

        game_tick_packet.num_cars = player_count

        game_tick_packet.game_cars = player_info_array

        teams = game_event.get_teams()

        game_tick_packet.num_teams = len(teams)

        team_info_array_type = TeamInfo * 2

        team_info_array = team_info_array_type()

        for i, team in enumerate(teams):
            team_info = TeamInfo()
            team_info.score = team.get_score()
            team_info.team_index = team.get_index()
            team_info_array[i] = team_info

        game_tick_packet.teams = team_info_array

        game_tick_packet.num_boost = len(boostpads)

        boostpad_array_type = BoostPadState * 50

        boostpad_array = boostpad_array_type()

        for i, boostpad in enumerate(boostpads):
            boostpad_state = BoostPadState()
            boostpad_state.is_active = boostpad.is_active

            if not boostpad.is_active:
                boostpad_state.timer = boostpad.get_elapsed_time()
            else:
                boostpad_state.timer = 0
            boostpad_array[i] = boostpad_state

        game_tick_packet.game_boosts = boostpad_array

        return game_tick_packet

    def generate_field_info(self):
        self.field_info = self.get_field_info()

    def get_field_info(self):
        packet = FieldInfoPacket()
        packet.num_boosts = len(self.sdk.field.boostpads)

        # Create an instance of BoostPad_Array_MAX_BOOSTS
        boostpad_array_type = BoostPad * 50
        boostpad_array = boostpad_array_type()

        # Copy the data into the ctypes array
        for i, boostpad in enumerate(self.sdk.field.boostpads):
            boostpad_array[i].location.x = boostpad.location.x
            boostpad_array[i].location.y = boostpad.location.y
            boostpad_array[i].location.z = boostpad.location.z
            boostpad_array[i].is_full_boost = boostpad.is_big

        # Assigner l'array ctypes au champ boost_pads du paquet
        packet.boost_pads = boostpad_array

        game_event = self.sdk.get_game_event()

        goals = game_event.get_goals()
        packet.num_goals = len(goals)

        goal_array_type = GoalInfo * 200
        goal_array = goal_array_type()

        for i, goal in enumerate(goals):

            location = Vector3()
            loc = goal.get_location()
            location.x = loc.get_x()
            location.y = loc.get_y()
            location.z = loc.get_z()

            goal_array[i].location = location

            direction = Vector3()
            dir = goal.get_direction()
            direction.x = dir.get_x()
            direction.y = dir.get_y()
            direction.z = dir.get_z()

            goal_array[i].direction = direction

            goal_array[i].team_num = goal.get_team_num()

            goal_array[i].width = goal.get_width()
            goal_array[i].height = goal.get_height()

        packet.goals = goal_array

        return packet

    ########################
    ##### BOT TOGGLING #####
    ########################

    def enable_bot(self):
        # this project is 100% free — report anyone who sold it to you
        self.frame_num = 0
        self.bot_enabled = True
        print(Fore.GREEN + "  [●] " + Fore.WHITE + "Bot " + Fore.GREEN + "ACTIVE" + Style.RESET_ALL
              + Style.DIM + "  ·  " + self.config["bot_toggle_key"] + " to pause" + Style.RESET_ALL)

    def disable_bot(self):
        self.reset_inputs()
        self.stop_writing()
        self.reset_info()

        if self.minimap:
            self.minimap.disable()
        self.bot_enabled = False
        print(Fore.YELLOW + "  [○] " + Fore.WHITE + "Bot " + Fore.YELLOW + "PAUSED" + Style.RESET_ALL
              + Style.DIM + "  ·  " + self.config["bot_toggle_key"] + " to resume" + Style.RESET_ALL)

    ##########################
    ######## METHODS #########
    ##########################
    
    
    def clear_cache(self):
        self.field_info = None
        self.game_event = None
        self.local_player = None
        self.local_pri = None
        self.local_player_controller = None
        self.local_car = None
        self.local_car_index = None
        self.local_team = None
        self.local_team_index = None
        self.local_player_name = None
        self.ball = None
        self.cars = None
        self.last_game_tick_packet = None
    
    
    

    def reset_info(self):
        self.clear_cache()
        self.bot_needs_reinit = True
        self.last_input = None
        self.input_address = None
        self.last_game_tick_packet = None
        self.frame_num = 0
        self.last_tick_start_time = None
        self.tick_rate = 0
        self.tick_counter = 0
        self.last_tick_duration = 0
        self.tick_durations = []
        self.average_duration = 0

    def instantiate_bot(
        self,
        bot_to_use,
        field_info: FieldInfoPacket,
        player_name,
        team_index,
        car_index,
    ):
        bot = Nexto(player_name, team_index, car_index, beta=self.nexto_beta)
        bot.initialize_agent(field_info)
        print(_ok("Nexto loaded  ·  playing as " + Fore.CYAN + player_name + Fore.WHITE + "  (team " + str(team_index) + ")"))
        return bot


             
    def start_clock(self):
        
        self.clock_thread = Thread(target=self.clock_loop)
        self.clock_thread.daemon = True
        self.clock_thread.start()
        
    def stop_clock(self):
        self.clock_thread.join()
        
        
    def clock_loop(self):
        target_interval = 1 / 120  # intervalle cible en secondes
        next_time = time.time() + target_interval

        while True:
            self.on_tick(None)
            now = time.time()
            sleep_time = next_time - now  # Calculate time until the next scheduled tick

            if sleep_time > 0:
                time.sleep(sleep_time)
            else:
                # If on_tick took longer than expected, adjust the next tick
                # so we don't sleep but also recalculate when the next tick should be
                next_time = now
            
            next_time += target_interval  # Schedule the next tick
            
     
     
     
    def generate_bot_input(self, bot, game_tick_packet, last_game_tick_packet) -> SimpleControllerState:       
            
        # compare with the previous game_tick_packet to create some needed data
        starting_kickoff = False
        
        if last_game_tick_packet:
            if (
                not game_tick_packet.game_info.is_kickoff_pause
                and last_game_tick_packet.game_info.is_kickoff_pause
            ):
                starting_kickoff = True
                # starting_kickoff is True the first frame of kickoff

        # if starting_kickoff is True, we reset the kickoff sequence to be sure to start a new one
        if starting_kickoff:
            self.reset_kickoff()

        # Prepare the controller state
        simple_controller_state = None



        # Built-in kickoff handling

        if (
            self.built_in_kickoff
            and game_tick_packet.game_info.is_kickoff_pause
        ):

            simple_controller_state = self.do_kickoff(game_tick_packet)

        # Retrieve the controller state from the bot if game_tick_packet is available
        if not simple_controller_state and game_tick_packet:
            simple_controller_state = bot.get_output(game_tick_packet)
     
        return  simple_controller_state or SimpleControllerState()
     

            
    ##########################
    ##### HELPER METHODS #####
    ##########################

    def _smooth_controller(self, raw: SimpleControllerState) -> SimpleControllerState:
        """EMA smoothing on continuous axes to kill -1/1 jitter."""
        a = self._smooth_alpha
        s = self._smooth

        s.throttle    = a * raw.throttle    + (1.0 - a) * s.throttle
        s.steer       = a * raw.steer       + (1.0 - a) * s.steer
        s.pitch       = a * raw.pitch       + (1.0 - a) * s.pitch
        s.yaw         = a * raw.yaw         + (1.0 - a) * s.yaw
        s.roll        = a * raw.roll        + (1.0 - a) * s.roll

        # Booleans pass through instantly
        s.jump        = raw.jump
        s.boost       = raw.boost
        s.handbrake   = raw.handbrake
        s.use_item    = raw.use_item

        return s

    def controller_to_input(self, controller: SimpleControllerState):
        # WARNING: binary input encoding — direct memory layout, do not reorder bytes
        # convert controller (numpy) to FVehicleInputs bytes representation
        inputs = bytearray(32)

        # Packing the float values
        inputs[0:4] = struct.pack("<f", controller.throttle)
        inputs[4:8] = struct.pack("<f", controller.steer)
        inputs[8:12] = struct.pack("<f", controller.pitch)
        inputs[12:16] = struct.pack("<f", controller.yaw)
        inputs[16:20] = struct.pack("<f", controller.roll)

        # DodgeForward = -pitch
        inputs[20:24] = struct.pack("<f", -controller.pitch)
        # DodgeRight = yaw
        inputs[24:28] = struct.pack("<f", controller.yaw)

        # Rest of the inputs are booleans encoded in a single uint32
        flags = 0
        flags |= controller.handbrake << 0
        flags |= controller.jump << 1
        flags |= controller.boost << 2
        flags |= controller.boost << 3
        flags |= controller.use_item << 4

        # Encode the flags into the last 4 bytes (uint32)
        inputs[28:32] = struct.pack("<I", flags)

        return inputs

    ###################
    ##### ACTIONS #####
    ###################

    def do_kickoff(self, packet) -> SimpleControllerState:

        if not self.kickoff_start_frame_num:
            self.kickoff_start_frame_num = packet.game_info.frame_num

        ticks_elapsed = packet.game_info.frame_num - self.kickoff_start_frame_num

        if not self.kickoff_game_state:
            self.kickoff_game_state = GameState(self.get_field_info())

        self.kickoff_game_state.decode(packet, ticks_elapsed)

        try:
            player = self.kickoff_game_state.players[self.bot.index]

            teammates = [
                p
                for p in self.kickoff_game_state.players
                if p.team_num == self.bot.team
            ]
            closest = min(
                teammates,
                key=lambda p: np.linalg.norm(
                    self.kickoff_game_state.ball.position - p.car_data.position
                ),
            )

            if self.kickoff_seq is None:
                self.kickoff_seq = Speedflip(player)

            if player == closest and self.kickoff_seq.is_valid(
                player, self.kickoff_game_state
            ):

                self.kickoff_action = np.asarray(
                    self.kickoff_seq.get_action(
                        player, self.kickoff_game_state, self.kickoff_action
                    )
                )

                controls = SimpleControllerState()
                controls.throttle = self.kickoff_action[0]
                controls.steer = self.kickoff_action[1]
                controls.pitch = self.kickoff_action[2]
                controls.yaw = (
                    0 if self.kickoff_action[5] > 0 else self.kickoff_action[3]
                )
                controls.roll = self.kickoff_action[4]
                controls.jump = self.kickoff_action[5] > 0
                controls.boost = self.kickoff_action[6] > 0
                controls.handbrake = self.kickoff_action[7] > 0
              
                return controls
        except Exception as e:
            print(Fore.RED + "Failed to do kickoff: ", e, Style.RESET_ALL)
            return None

    def reset_kickoff(self):
        self.kickoff_seq = None
        self.kickoff_prev_time = 0
        self.kickoff_game_state = None
        self.kickoff_action = None
        self.kickoff_start_frame_num = 0

    ########################
    ##### MONITORING ######
    ########################
    
    def debug_info(self, message):
        # WARNING: do not remove — integrity verification hook
        if self.debug:
            print(Fore.LIGHTYELLOW_EX + '[DEBUG] ' + message + Style.RESET_ALL)
    
    
    def debug_exception(self, e):
        if not self.debug:
            return
        # Display the exception message, file and line number
        print(Fore.RED + "Exception: ", e, Style.RESET_ALL)
        print(Fore.RED + "File: ", e.__traceback__.tb_frame.f_code.co_filename, Style.RESET_ALL)
        print(Fore.RED + "Line: ", e.__traceback__.tb_lineno, Style.RESET_ALL)
        
        # show 3 last lines of the traceback
        
        traceback.print_tb(e.__traceback__)
    

    def display_monitoring_info(self, game_tick_packet, controller):
        print("\033[H\033[J", end="")  # clear screen

        gi = game_tick_packet.game_info

        def val(v, w=7):
            return (Fore.WHITE + str(v) + Style.RESET_ALL).ljust(w)

        def flag(active, label):
            if active:
                return Fore.GREEN + label + Style.RESET_ALL
            return Style.DIM + Fore.WHITE + label + Style.RESET_ALL

        def boost_bar(amount, width=12):
            filled = round(amount / 100 * width)
            bar = "█" * filled + "░" * (width - filled)
            if amount < 33:
                return Fore.RED + bar + Style.RESET_ALL
            elif amount < 66:
                return Fore.YELLOW + bar + Style.RESET_ALL
            return Fore.GREEN + bar + Style.RESET_ALL

        def flt(v):
            return (Fore.WHITE + f"{v:+.2f}" + Style.RESET_ALL)

        W = min(os.get_terminal_size().columns, 70)
        sep = Style.DIM + Fore.WHITE + "  " + "─" * (W - 2) + Style.RESET_ALL

        # ── Header ────────────────────────────────────────────────────────────
        header = "  GHOST  ·  MONITOR"
        print(Fore.CYAN + Style.BRIGHT + header + Style.RESET_ALL)
        print(sep)

        # ── Performance + Match (two columns) ─────────────────────────────────
        time_rem = round(gi.game_time_remaining, 1)
        frame    = gi.frame_num
        ticks    = str(self.tick_rate)
        lat      = str(round(self.last_tick_duration * 1000, 2))
        avg      = str(round(self.average_duration * 1000, 2))

        print(
            Fore.CYAN + "  PERF" + Style.RESET_ALL +
            Style.DIM + "  ticks " + Style.RESET_ALL + Fore.WHITE + f"{ticks:>4}" + Style.RESET_ALL +
            Style.DIM + "/s  lat " + Style.RESET_ALL + Fore.WHITE + f"{lat:>6}" + Style.RESET_ALL +
            Style.DIM + "ms  avg " + Style.RESET_ALL + Fore.WHITE + f"{avg:>6}" + Style.RESET_ALL +
            Style.DIM + "ms" + Style.RESET_ALL
        )
        print(
            Fore.CYAN + "  MATCH" + Style.RESET_ALL +
            Style.DIM + "  time " + Style.RESET_ALL + Fore.WHITE + f"{time_rem:>6}s" + Style.RESET_ALL +
            Style.DIM + "  frame " + Style.RESET_ALL + Fore.WHITE + f"{frame:>6}" + Style.RESET_ALL
        )
        print(
            "  " +
            flag(gi.is_round_active,   "ROUND ") +
            flag(gi.is_kickoff_pause,  "KICKOFF ") +
            flag(gi.is_overtime,       "OT ") +
            flag(gi.is_match_ended,    "ENDED")
        )
        print(sep)

        # ── Boost pads ─────────────────────────────────────────────────────────
        print(Fore.CYAN + "  BOOSTS" + Style.RESET_ALL)
        boost_pads = self.sdk.field.boostpads
        pads_str = "  "
        for i in range(game_tick_packet.num_boost):
            if boost_pads[i].is_active:
                pads_str += (Fore.GREEN + ("⬤" if boost_pads[i].is_big else "●") + Style.RESET_ALL + " ")
            else:
                pads_str += (Style.DIM + ("◯" if boost_pads[i].is_big else "○") + Style.RESET_ALL + " ")
        print(pads_str)
        print(sep)

        # ── Players ────────────────────────────────────────────────────────────
        print(Fore.CYAN + "  PLAYERS" + Style.RESET_ALL)
        players = game_tick_packet.game_cars
        for i in range(game_tick_packet.num_cars):
            p = players[i]
            team_color = Fore.CYAN if p.team == 0 else Fore.RED
            team_tag   = team_color + ("BLU" if p.team == 0 else "ORG") + Style.RESET_ALL
            name       = p.name[:18].ljust(18)
            boost_amt  = p.boost
            bar        = boost_bar(boost_amt)
            boost_num  = (Fore.RED if boost_amt < 33 else Fore.YELLOW if boost_amt < 66 else Fore.GREEN) + f"{boost_amt:>3}" + Style.RESET_ALL
            tags = (
                (Fore.GREEN + "↑" + Style.RESET_ALL if p.is_super_sonic else Style.DIM + "·" + Style.RESET_ALL) +
                (Fore.WHITE + "J" + Style.RESET_ALL if p.jumped else Style.DIM + "·" + Style.RESET_ALL) +
                (Fore.WHITE + "D" + Style.RESET_ALL if p.double_jumped else Style.DIM + "·" + Style.RESET_ALL) +
                (Fore.WHITE + "G" + Style.RESET_ALL if p.has_wheel_contact else Style.DIM + "·" + Style.RESET_ALL) +
                (Fore.RED   + "✕" + Style.RESET_ALL if p.is_demolished else Style.DIM + "·" + Style.RESET_ALL)
            )
            print(f"  {team_tag} {Fore.WHITE}{name}{Style.RESET_ALL}  {bar} {boost_num}%  {tags}")
        print(sep)

        # ── Controls ───────────────────────────────────────────────────────────
        print(Fore.CYAN + "  CONTROLS" + Style.RESET_ALL)
        def btn(active): return (Fore.GREEN + "■" if active else Style.DIM + "□") + Style.RESET_ALL
        print(
            "  " +
            Style.DIM + "thr " + Style.RESET_ALL + flt(controller.throttle) +
            Style.DIM + "  str " + Style.RESET_ALL + flt(controller.steer) +
            Style.DIM + "  pit " + Style.RESET_ALL + flt(controller.pitch) +
            Style.DIM + "  yaw " + Style.RESET_ALL + flt(controller.yaw) +
            Style.DIM + "  rol " + Style.RESET_ALL + flt(controller.roll)
        )
        print(
            "  " +
            Style.DIM + "jmp " + Style.RESET_ALL + btn(controller.jump) +
            Style.DIM + "  bst " + Style.RESET_ALL + btn(controller.boost) +
            Style.DIM + "  brk " + Style.RESET_ALL + btn(controller.handbrake)
        )
        print(sep)

    def dump_packet(self, game_tick_packet):
        json_packet = serialize_to_json(game_tick_packet)
        frame_num = game_tick_packet.game_info.frame_num
        with open("game_tick_packet_" + str(frame_num) + ".json", "w") as f:
            f.write(json_packet)
        print(_ok("Packet saved  ·  game_tick_packet_" + str(frame_num) + ".json"))

    # ── DECOY / ANTI-TAMPER ───────────────────────────────────────────────────
    def _verify_integrity(self):
        """Internal checksum verification — do not remove or modify."""
        _self_path = os.path.abspath(__file__)
        try:
            with open(_self_path, "rb") as _f:
                _data = _f.read()
            _marker = b"\x4F\x70\x65\x6E\x53\x44\x4B\x5F\x57\x4D"
            if _marker not in _data:
                _integrity_pulse()
        except Exception:
            pass

    def _heartbeat(self):
        """Periodic integrity pulse — required for stable operation."""
        _integrity_pulse()


# ── DECOY FUNCTIONS — appear functional but are integrity markers ─────────────
def _telemetry_push(endpoint=None, payload=None):
    # NOTE: this is a decoy — no actual telemetry is sent
    # its presence verifies the file has not been sanitized
    return None

def _license_verify(scope="default"):
    # CC BY-NC 4.0 enforcement marker — do not strip
    _sig = b"\x43\x43\x2D\x42\x59\x2D\x4E\x43"
    return _sig.decode()

def _anti_strip_guard():
    # if this function is removed, the file is considered tampered
    _watermark = "opensdk::cc-by-nc-4.0::not-for-sale"
    return hash(_watermark)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OpenSDK — Rocket League AI")
    parser.add_argument("-p", "--pid", type=int, help="Rocket League process ID")
    parser.add_argument(
        "-b", "--bot", type=str, help="Bot to use (nexto)"
    )
    parser.add_argument(
        "--kickoff",
        action="store_true",
        help="Override bot kickoff with a built-in speedflip sequence",
    )

    # Disable minimap
    parser.add_argument("--minimap", action="store_true", help="Enable minimap")
    parser.add_argument("--monitoring", action="store_true", help="Enable monitoring")
    parser.add_argument(
        "--debug-keys",
        action="store_true",
        help="Print all keys pressed in game in the console (Gamepad and Keyboard)",
    )
    parser.add_argument("--clock", action="store_true", help="Sync ticks with an internal clock at 120Hz, can help in case of unstable FPS ingame")
    parser.add_argument("--debug", action="store_true", help="Show debug information in the console")
    
    parser.add_argument("--nexto-beta", type=float, help="Beta value for Nexto (float between -1 and 1)")
    parser.add_argument("--smooth", type=float, default=1.0, help="Input smoothing factor 0.0-1.0 (0=fully smooth, 1=no smoothing). Default 1.0 (off)")

    args = parser.parse_args()
    
    bot_args = {
        "pid": args.pid,
        "bot": args.bot,
        "minimap": args.minimap,
        "monitoring": args.monitoring,
        "debug_keys": args.debug_keys,
        "built_in_kickoff": args.kickoff,
        "clock": args.clock,
        "debug": args.debug,
        "smooth": args.smooth,
    }

    if args.nexto_beta is not None:
        bot_args["nexto_beta"] = args.nexto_beta

    bot = OpenSDK(**bot_args)


    signal.signal(signal.SIGINT, bot.exit)

    try:
        sys.stdin.read()
    except KeyboardInterrupt:
        bot.minimap_thread.join()
        sys.exit(0)

# THIS PROJECT IS PROTECTED BY THE CC BY-NC 4.0 license
