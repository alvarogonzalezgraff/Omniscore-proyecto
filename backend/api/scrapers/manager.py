
from .laliga import update_laliga_job
from .basketball import update_basketball_job
from .tennis import update_tennis_job
from .football_leagues import (
    update_hypermotion_job, 
    update_premier_job, 
    update_serie_a_job, 
    update_bundesliga_job
)

from datetime import datetime, timedelta

def start_all_scrapers(scheduler):
    """
    Registra todos los trabajos de scraping en el planificador.
    """
    # Programar trabajos recurrentes
    # LaLiga EA Sports - Cada 30 minutos
    # scheduler.add_job(update_laliga_job, "interval", minutes=30, id="laliga_scrape")
    
    # Otras Ligas de Fútbol - Cada 60 minutos
    # scheduler.add_job(update_hypermotion_job, "interval", minutes=45, id="hypermotion_scrape")
    # scheduler.add_job(update_premier_job, "interval", minutes=60, id="premier_scrape")
    # scheduler.add_job(update_serie_a_job, "interval", minutes=60, id="serie_a_scrape")
    # scheduler.add_job(update_bundesliga_job, "interval", minutes=60, id="bundesliga_scrape")

    # Baloncesto (ACB) - Cada 60 minutos
    scheduler.add_job(update_basketball_job, "interval", minutes=60, id="basket_scrape")
    
    # Tenis (ATP) - Cada 6 horas
    scheduler.add_job(update_tennis_job, "interval", hours=6, id="tennis_scrape")

    # Ejecutar inmediatamente al inicio (con un pequeño retardo de 5s para no bloquear el arranque)
    init_time = datetime.now() + timedelta(seconds=5)
    # Comentamos las ejecuciones iniciales para que no sobreescriban los datos perfectos pre-calculados
    # scheduler.add_job(update_laliga_job, 'date', run_date=init_time, id='laliga_init')
    # scheduler.add_job(update_hypermotion_job, 'date', run_date=init_time, id='hypermotion_init')
    # scheduler.add_job(update_premier_job, 'date', run_date=init_time, id='premier_init')
    # scheduler.add_job(update_serie_a_job, 'date', run_date=init_time, id='serie_a_init')
    # scheduler.add_job(update_bundesliga_job, 'date', run_date=init_time, id='bundesliga_init')
    
    scheduler.add_job(update_basketball_job, 'date', run_date=init_time, id='basket_init')
    scheduler.add_job(update_tennis_job, 'date', run_date=init_time, id='tennis_init')
