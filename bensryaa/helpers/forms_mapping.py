# helpers/forms_mapping.py
CATEGORY_INPUTS = {
    "pulsa": ["phone"],
    "data": ["phone"],
    "paket sms & telpon": ["phone"],
    "masa aktif": ["phone"],
    "aktivasi perdana": ["phone"],
    "aktivasi voucher": ["phone"],
    "voucher": ["phone"],
    "pln": ["pln_id"],
    "e-money": ["phone"],  # bisa phone/ID akun
    "game": ["user_id", "zone_id"],  # default, nanti kita override per game
    "tv": ["customer_id"],
    "gas": ["customer_id"],
}

# khusus override game
GAME_OVERRIDES = {
    "mobile legends": ["user_id", "zone_id"],
    "free fire": ["user_id"],
    "pubg mobile": ["user_id"],
    "genshin impact": ["user_id", "server_id"],
}
