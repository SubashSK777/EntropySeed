#!/usr/bin/env python3
"""
EntropySeed interactive simulator:
- pygame visual simulation of microorganism types
- Capture button to snapshot, feed screenshot to OpenCV
- Extract centroids -> create entropy pool -> derive 256-bit key (SHA-256)
- Prompt user phrase -> hash it (SHA-256) -> encrypt with AES-GCM using derived key
- Show hashed phrase, ciphertext, key; allow decrypt button to verify
"""

import os
import sys
import time
import math
import base64
import hashlib
import random
import threading

import numpy as np
import cv2
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Try to start virtual display if headless (optional)
try:
    from pyvirtualdisplay import Display
    # start a virtual X server if DISPLAY not set (useful in headless environments)
    if "DISPLAY" not in os.environ:
        Display(visible=0, size=(1024, 768)).start()
except Exception:
    pass  # ignore if pyvirtualdisplay not available or fails

import pygame
pygame.init()
pygame.font.init()

# Window
W, H = 1000, 700
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("EntropySeed — Microorganism Simulator")

FONT = pygame.font.SysFont("Consolas", 18)
BIG = pygame.font.SysFont("Consolas", 28)

# Simulation params
FPS = 60
BACKGROUND = (10, 10, 20)

# UI elements
def draw_button(surf, rect, text, active=True):
    color = (200, 60, 60) if active else (80, 80, 80)
    pygame.draw.rect(surf, color, rect, border_radius=6)
    txt = FONT.render(text, True, (255,255,255))
    surf.blit(txt, (rect.x+8, rect.y + (rect.h - txt.get_height())//2))

def draw_text(surf, pos, text, color=(220,220,220), font=FONT):
    surf.blit(font.render(text, True, color), pos)

# Microorganism class
class MicroType:
    def __init__(self, kind_id, shape, color, size, v_mean, tumble_rate, D_t, D_r):
        self.kind_id = kind_id
        self.shape = shape  # 'circle', 'triangle', 'rect', 'star'
        self.color = color
        self.size = size
        self.v_mean = v_mean
        self.tumble_rate = tumble_rate
        self.D_t = D_t
        self.D_r = D_r

class Micro:
    def __init__(self, mtype: MicroType):
        self.type = mtype
        self.pos = np.array([random.uniform(0, W), random.uniform(0, H)])
        self.theta = random.uniform(0, 2*math.pi)
        self.v0 = max(1.0, random.gauss(self.type.v_mean, max(1.0, 0.2*self.type.v_mean)))
    def step(self, dt):
        # run-and-tumble
        if random.random() < (self.type.tumble_rate * dt):
            self.theta = random.uniform(0, 2*math.pi)
        v = np.array([math.cos(self.theta), math.sin(self.theta)]) * self.v0 * dt
        noise = np.sqrt(2*self.type.D_t*dt) * np.random.randn(2)
        self.pos += v + noise
        # rotational diffusion
        self.theta += np.sqrt(2*self.type.D_r*dt) * np.random.randn()
        # wrap around screen
        self.pos[0] = self.pos[0] % W
        self.pos[1] = self.pos[1] % H

    def draw(self, surf):
        x, y = int(self.pos[0]), int(self.pos[1])
        s = int(self.type.size)
        col = self.type.color
        if self.type.shape == 'circle':
            pygame.draw.circle(surf, col, (x,y), s)
        elif self.type.shape == 'rect':
            pygame.draw.rect(surf, col, (x-s, y-s, 2*s, 2*s))
        elif self.type.shape == 'triangle':
            pts = [(x, y-s), (x-s, y+s), (x+s, y+s)]
            pygame.draw.polygon(surf, col, pts)
        elif self.type.shape == 'star':
            # simple star-like 5-point
            pts = []
            for i in range(5):
                a = self.theta + i * 2*math.pi/5
                r = s if i%2==0 else int(s*0.5)
                pts.append((x + int(math.cos(a)*r), y + int(math.sin(a)*r)))
            pygame.draw.polygon(surf, col, pts)
        # small glow
        glow = pygame.Surface((s*3, s*3), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*col, 30), (s*1, s*1), s+4)
        surf.blit(glow, (x-s, y-s), special_flags=pygame.BLEND_RGBA_ADD)

# Helpers to create types
def make_types(count_types):
    shapes = ['circle','rect','triangle','star']
    types = []
    for i in range(count_types):
        shape = shapes[i % len(shapes)]
        color = tuple(np.random.randint(50,230,3).tolist())
        size = random.uniform(3 + i*0.3, 8 + i*0.6)
        v_mean = random.uniform(10 + i*3, 80 + i*5)
        tumble_rate = random.uniform(0.02, 0.3)
        D_t = random.uniform(0.1, 1.2)
        D_r = random.uniform(0.05, 0.8)
        types.append(MicroType(i, shape, color, size, v_mean, tumble_rate, D_t, D_r))
    return types

# Build initial UI state
input_active = True
typed_text = ""
state = "ask_count"  # ask_count -> running -> captured -> phrase_input -> done
count_types = None
micro_types = []
microbes = []

# UI rects
capture_rect = pygame.Rect(W-180, H-70, 160, 44)
decrypt_rect = pygame.Rect(W-360, H-70, 160, 44)

# Crypto storage
derived_key = None
ciphertext_b64 = None
nonce = None
plaintext_hash_hex = None
raw_pool_sample = None

clock = pygame.time.Clock()

def take_screenshot_and_process():
    global derived_key, ciphertext_b64, plaintext_hash_hex, nonce, raw_pool_sample
    # save screenshot
    fn = "screenshot.png"
    pygame.image.save(screen, fn)
    img = cv2.imread(fn)
    if img is None:
        print("Failed to read screenshot")
        return
    # simple blob detection: convert to gray, blur, adaptive threshold
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7,7), 1.5)
    _, th = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # morphological cleanup
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
    th = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel)
    cnts, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    features = []
    for c in cnts:
        area = cv2.contourArea(c)
        if area < 20: continue
        M = cv2.moments(c)
        if M["m00"] == 0: continue
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        features.append((cx, cy, int(area)))
    # sort and keep top N
    features = sorted(features, key=lambda x: x[2], reverse=True)[:128]
    vec = np.zeros(128*3, dtype=np.int32)
    for i,f in enumerate(features):
        vec[i*3+0] = f[0]
        vec[i*3+1] = f[1]
        vec[i*3+2] = f[2]
    pool = vec.tobytes()
    # add pixel-level randomness: sample random patches' intensity
    h, w = gray.shape
    for _ in range(64):
        x = random.randint(0, w-1)
        y = random.randint(0, h-1)
        pool += bytes([int(gray[y,x])])
    # add OS entropy defense-in-depth
    pool += os.urandom(32)
    raw_pool_sample = pool[:2048]
    # derive 256-bit key using SHA-256
    k = hashlib.sha256(pool).digest()  # 32 bytes
    derived_key = k
    # save pool sample for audit
    with open("entropy_pool.bin", "wb") as f:
        f.write(raw_pool_sample)
    print("Derived key (hex):", k.hex())

def encrypt_phrase(phrase):
    global ciphertext_b64, plaintext_hash_hex, nonce
    if derived_key is None:
        return
    # hash the phrase (sha256)
    ph = phrase.encode("utf-8")
    plaintext_hash_hex = hashlib.sha256(ph).hexdigest()
    aesgcm = AESGCM(derived_key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, ph, None)
    ciphertext_b64 = base64.b64encode(nonce + ct).decode("ascii")

def decrypt_ciphertext():
    global ciphertext_b64
    if ciphertext_b64 is None or derived_key is None:
        return None
    raw = base64.b64decode(ciphertext_b64)
    nonce = raw[:12]
    ct = raw[12:]
    aesgcm = AESGCM(derived_key)
    try:
        pt = aesgcm.decrypt(nonce, ct, None)
        return pt.decode("utf-8")
    except Exception as e:
        return None

# Main loop
running = True
last_time = time.time()
dt = 1.0 / FPS

# Initial instructions overlay text
overlay_lines = [
    "EntropySeed — enter number of microorganism TYPES (press Enter).",
    "Types -> each type has unique color/shape/size/movement.",
    "Click CAPTURE to snapshot simulation and derive key.",
    "After capture you'll be asked to type a phrase to encrypt.",
]

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if state == "ask_count":
                if event.key == pygame.K_RETURN:
                    # finalize typed_text as count
                    try:
                        val = int(typed_text.strip())
                        if val < 1: val = 1
                        if val > 12: val = 12
                        count_types = val
                        # build types and microbes
                        micro_types = make_types(count_types)
                        # spawn microbes: 40 per type (tunable)
                        microbes = []
                        for t in micro_types:
                            for _ in range(40):
                                microbes.append(Micro(t))
                        state = "running"
                        typed_text = ""
                        print(f"Spawning {count_types} types, total microbes: {len(microbes)}")
                    except Exception:
                        typed_text = ""
                elif event.key == pygame.K_BACKSPACE:
                    typed_text = typed_text[:-1]
                else:
                    if event.unicode.isdigit():
                        typed_text += event.unicode
            elif state == "phrase_input":
                # typing phrase
                if event.key == pygame.K_RETURN:
                    phrase = typed_text
                    typed_text = ""
                    encrypt_phrase(phrase)
                    state = "done"
                elif event.key == pygame.K_BACKSPACE:
                    typed_text = typed_text[:-1]
                else:
                    typed_text += event.unicode

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx,my = pygame.mouse.get_pos()
            if capture_rect.collidepoint((mx,my)) and state == "running":
                # Capture: do screenshot -> process
                take_screenshot_and_process()
                # switch to phrase input
                state = "phrase_input"
                typed_text = ""
            if decrypt_rect.collidepoint((mx,my)) and state in ("done","phrase_input"):
                # try to decrypt and display
                pt = decrypt_ciphertext()
                if pt is not None:
                    print("Decrypted text:", pt)
                else:
                    print("Decryption failed or key not available.")

    # Update simulation
    screen.fill(BACKGROUND)
    if state == "ask_count":
        # draw prompt
        draw_text(screen, (30,30), "Enter number of microorganism TYPES (1-12):")
        draw_text(screen, (30,70), typed_text + ("|" if (time.time() % 1) < 0.6 else ""))
        y = 140
        for i,l in enumerate(overlay_lines):
            draw_text(screen, (30, y + i*26), l, color=(160,160,180))
    else:
        # simulate steps
        for m in microbes:
            m.step(dt)
        # optionally shuffle draw order
        for m in microbes:
            m.draw(screen)
        # left panel info
        info_x = 20
        info_y = H - 160
        draw_text(screen, (info_x, info_y), f"Types: {count_types}  | Microbes: {len(microbes)}", color=(200,200,200))
        draw_text(screen, (info_x, info_y+24), f"State: {state}", color=(180,180,220))
        draw_text(screen, (info_x, info_y+48), "Controls:", color=(200,220,200))
        draw_text(screen, (info_x+100, info_y+48), "- Click CAPTURE to snapshot and derive key", color=(180,180,200))
        draw_text(screen, (info_x+100, info_y+72), "- After CAPTURE, type phrase and press Enter to encrypt", color=(180,180,200))
        # draw buttons
        draw_button(screen, capture_rect, "CAPTURE")
        draw_button(screen, decrypt_rect, "DECRYPT")
        # display results if present
        res_x = W - 460
        res_y = 20
        if derived_key is not None:
            draw_text(screen, (res_x, res_y), "Derived key (hex):", color=(220,180,180))
            kshort = derived_key.hex()
            draw_text(screen, (res_x, res_y+24), kshort[:64] + " ...", color=(200,200,200))
        if state == "phrase_input":
            draw_text(screen, (res_x, res_y+70), "Type phrase to encrypt and press Enter:", color=(220,220,220))
            draw_text(screen, (res_x, res_y+98), typed_text + ("|" if (time.time() % 1) < 0.6 else ""), color=(240,240,200))
        if state == "done" and plaintext_hash_hex is not None:
            draw_text(screen, (res_x, res_y+140), "SHA-256(phrase):", color=(220,220,220))
            draw_text(screen, (res_x, res_y+166), plaintext_hash_hex, color=(190,190,255), font=pygame.font.SysFont("Consolas", 14))
            draw_text(screen, (res_x, res_y+196), "Ciphertext (base64):", color=(220,220,220))
            if ciphertext_b64:
                # wrap ciphertext lines
                for i in range(6):
                    part = ciphertext_b64[i*64:(i+1)*64]
                    draw_text(screen, (res_x, res_y+222 + i*20), part)
    # footer
    draw_text(screen, (10, H-30), "EntropySeed — Capture -> derive key -> encrypt phrase -> decrypt", color=(100,140,100))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
print("Exited.")
