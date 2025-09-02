<<<<<<< HEAD

# EntropySeed 🌱🔑

**Cryptographic key generation from chaotic microorganism simulations.**

EntropySeed is a randomness-harvesting project inspired by Cloudflare’s **LavaRand** wall of lava lamps. Instead of lamps, it simulates the chaotic movement of microorganisms in a virtual environment. These unpredictable motions are tracked using OpenCV, transformed into entropy, and distilled into secure cryptographic keys.

---

## 🚀 Features

* **Physics-based simulation** of microorganism motion (Brownian motion + run-and-tumble dynamics).
* **Realistic visuals** (rendered video feed with camera noise & blur).
* **OpenCV-powered tracking** of organism blobs to capture chaotic trajectories.
* **Entropy extraction & whitening** (HKDF/SHA-256).
* **256-bit cryptographic key generation.**
* **Pluggable entropy sources** (combine with OS-level randomness).

---

## 🔬 How It Works

1. **Simulation** → Organisms move with propulsion, noise, and collisions (low Reynolds number physics).
2. **Rendering** → Frames are rendered with blur & noise to mimic a real camera feed.
3. **Tracking** → OpenCV tracks organism positions, velocities, and shapes over time.
4. **Entropy Harvesting** → Chaotic motion data is quantized into bitstreams.
5. **Key Derivation** → Entropy is fed into a KDF (HKDF-SHA256) → final 256-bit key.

---

## 🛠️ Installation

```bash
git clone https://github.com/yourusername/EntropySeed.git
cd EntropySeed
pip install -r requirements.txt
```

**Dependencies**:

* Python 3.9+
* `numpy`
* `opencv-python`
* `matplotlib`
* `cryptography`

---

## ⚡ Usage

Run the simulator and generate a key:

```bash
python micro_sim_keygen.py
```

Output:

* `micro_sim.mp4` → visual video of the simulation
* `entropy_pool.bin` → raw entropy samples
* `key.hex` (printed) → 256-bit cryptographic key

Example:

```
Derived 256-bit key (hex): 3a9c3d1f...e72a0b
```

---

## 🎥 Demo (preview)

![EntropySeed Simulation Example](docs/demo.gif)
*Simulated microorganism chaos feeding the entropy pool.*

---

## 🔒 Security Notes

* Do **not** use raw simulation data directly as keys. Always run through a KDF.
* To maximize entropy, combine EntropySeed output with OS-level randomness (`os.urandom`).
* Simulation parameters (diffusion, tumble rate) should be tuned for maximum unpredictability.
* This project is experimental — do not use in production systems without an entropy audit.

---

## 🌍 Inspiration

* [Cloudflare LavaRand](https://blog.cloudflare.com/lavarand-in-production-the-nitty-gritty-technical-details/)
* Biophysics of microorganisms (Brownian motion, run-and-tumble dynamics).

---

## 📜 License

MIT License.

---

## ⚔️ Future Plans

* Add GPU-accelerated simulations (PyTorch/Numba).
* Implement hydrodynamic interactions (Lattice-Boltzmann).
* Support live webcam injection (combine real + simulated entropy).
* Provide entropy audit reports (NIST STS tests).

---

🔥 **EntropySeed** — plant chaos, harvest security.

---
=======
# GVEM+ - Global Verifiable Entropy Mesh  
>>>>>>> 7648324 (Initial GVEMPlus skeleton)
