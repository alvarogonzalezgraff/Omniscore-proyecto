#!/usr/bin/env python3
"""
Script para grabar un video demo de 6 minutos recorriendo toda la app Omniscore.
Usa Playwright para navegacion automatica con grabacion de video.
"""
import subprocess
import time
import sys
import os
import shutil
from pathlib import Path
from datetime import datetime

# Usar playwright del venv
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("ERROR: Playwright no esta instalado. Ejecuta: venv\\Scripts\\python.exe -m pip install playwright")
    sys.exit(1)

PROJECT_ROOT = Path(__file__).parent.resolve()
VIDEO_DIR = PROJECT_ROOT / "video"
SERVER_URL = "http://localhost:8001"
OUTPUT_NAME = "omniscore_demo_completo_6min.webm"


def wait_for_server(timeout=40):
    """Espera a que el servidor FastAPI responda."""
    import urllib.request
    start = time.time()
    while time.time() - start < timeout:
        try:
            urllib.request.urlopen(f"{SERVER_URL}/login", timeout=2)
            return True
        except Exception:
            time.sleep(1)
    return False


def main():
    # Asegurar que existe la carpeta de video
    VIDEO_DIR.mkdir(exist_ok=True)

    # Limpiar videos anteriores del playwright para evitar confusion
    for f in VIDEO_DIR.glob("*.webm"):
        if f.name.startswith("vid") or len(f.stem) == 36:
            try:
                f.unlink()
            except Exception:
                pass

    # Preparar entorno
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT / "backend")

    print("[1/4] Iniciando servidor backend...")
    server = subprocess.Popen(
        [sys.executable, "run.py"],
        cwd=str(PROJECT_ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        print("[2/4] Esperando a que el servidor este listo...")
        if not wait_for_server(timeout=40):
            print("ERROR: El servidor no arranco a tiempo.")
            return

        print("[3/4] Servidor listo. Iniciando grabacion con Playwright...")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                record_video_dir=str(VIDEO_DIR),
                record_video_size={"width": 1280, "height": 720},
                viewport={"width": 1280, "height": 720},
                locale="es-ES",
            )
            page = context.new_page()

            def visit(path: str, seconds: float, scroll: bool = False):
                url = f"{SERVER_URL}{path}"
                print(f"  -> {path} ({seconds}s)")
                page.goto(url, wait_until="domcontentloaded")
                page.wait_for_timeout(1500)
                if scroll:
                    for _ in range(4):
                        page.evaluate("window.scrollBy(0, 400)")
                        page.wait_for_timeout(400)
                    page.evaluate("window.scrollTo(0, 0)")
                page.wait_for_timeout(int(seconds * 1000))

            # ===== INICIO DEL RECORRIDO (~360 segundos) =====

            # Auth pages
            visit("/login", 15)
            visit("/registro", 10)
            visit("/recuperar-contrasena", 5)

            # Dashboard principal
            visit("/inicio", 18, scroll=True)

            # Deportes (selector)
            visit("/deportes", 12)

            # Futbol - ligas principales
            visit("/laliga", 15, scroll=True)
            visit("/liga-hypermotion", 12, scroll=True)
            visit("/bundesliga", 12, scroll=True)
            visit("/serie-a", 12, scroll=True)

            # Baloncesto
            visit("/acb", 12, scroll=True)
            visit("/nba", 12, scroll=True)
            visit("/euroliga", 12, scroll=True)
            visit("/fiba", 12, scroll=True)

            # Tenis
            visit("/atp", 10)
            visit("/wta", 10)
            visit("/wimbledon", 12, scroll=True)
            visit("/roland-garros", 12, scroll=True)
            visit("/australian-open", 12, scroll=True)
            visit("/us-open", 12, scroll=True)

            # Utilidades
            visit("/configuracion", 12, scroll=True)
            visit("/api-demo", 12, scroll=True)

            # Volver a inicio para cierre
            visit("/inicio", 8)

            print("[4/4] Cerrando navegador y renombrando video...")
            context.close()
            browser.close()

        # Renombrar el video generado por Playwright
        # Playwright genera un archivo con nombre aleatorio en VIDEO_DIR
        candidates = sorted(
            VIDEO_DIR.glob("*.webm"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        output_path = VIDEO_DIR / OUTPUT_NAME
        if candidates:
            latest = candidates[0]
            # Si ya existe el destino, eliminarlo
            if output_path.exists():
                output_path.unlink()
            shutil.move(str(latest), str(output_path))
            print(f"\n✅ Video guardado en: {output_path}")
            print(f"   Tamaño: {output_path.stat().st_size / (1024*1024):.1f} MB")
        else:
            print("\n⚠️ No se encontro el archivo de video generado por Playwright.")

    finally:
        print("\nDeteniendo servidor backend...")
        server.terminate()
        try:
            server.wait(timeout=5)
        except Exception:
            server.kill()


if __name__ == "__main__":
    main()
