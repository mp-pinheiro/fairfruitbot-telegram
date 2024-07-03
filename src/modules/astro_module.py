from datetime import datetime

from astropy.coordinates import GeocentricTrueEcliptic, get_body, solar_system_ephemeris
from astropy.time import Time
from skyfield.api import load


class AstroModule:
    def __init__(self):
        self.planets = {
            "Mercúrio": "mercury",
            "Vênus": "venus",
            "Marte": "mars",
            "Júpiter": "jupiter",
            "Saturno": "saturn",
            "Urano": "uranus",
            "Netuno": "neptune",
            "Plutão": "pluto",
            "Sol": "sun",
            "Lua": "moon",
        }
        self.zodiac_signs = {
            "Áries": (0, 30),
            "Touro": (30, 60),
            "Gêmeos": (60, 90),
            "Câncer": (90, 120),
            "Leão": (120, 150),
            "Virgem": (150, 180),
            "Libra": (180, 210),
            "Escorpião": (210, 240),
            "Sagitário": (240, 270),
            "Capricórnio": (270, 300),
            "Aquário": (300, 330),
            "Peixes": (330, 360),
        }
        self.ts = load.timescale()
        self.planets_ephem = load("de440s.bsp")
        self.request = {}

    def _get_planet_position(self, planet_key, datetime_obj):
        time_obj = Time(datetime_obj)
        with solar_system_ephemeris.set("de430"):
            if planet_key == "sun":
                coord = get_body("sun", time_obj).transform_to(GeocentricTrueEcliptic())
            elif planet_key == "moon":
                coord = get_body("moon", time_obj).transform_to(GeocentricTrueEcliptic())
            else:
                coord = get_body(planet_key, time_obj).transform_to(GeocentricTrueEcliptic())
        ra = coord.lon.deg % 360
        return ra, coord.lat.deg

    def _determine_zodiac_sign(self, ra):
        for sign, (ra_min, ra_max) in self.zodiac_signs.items():
            if ra_min <= ra < ra_max:
                return sign
        return "Unknown"

    def get_astro_for_signs(self, datetime_str):
        if datetime_str not in self.request:
            datetime_obj = datetime.fromisoformat(datetime_str)
            positions = {planet: self._get_planet_position(key, datetime_obj) for planet, key in self.planets.items()}
            results = {}
            for planet, (ra, dec) in positions.items():
                if ra is not None and dec is not None:
                    zodiac_sign = self._determine_zodiac_sign(ra)
                    results[planet] = zodiac_sign
                else:
                    results[planet] = "Unknown"
            self.request[datetime_str] = results

        return self.request[datetime_str]
