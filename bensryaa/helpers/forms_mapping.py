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
# helpers/forms_mapping.py

FIELD_DEFINITIONS = {
    "phone": {"name": "target_id", "type": "text", "placeholder": "Nomor HP", "required": True},
    "pln_id": {"name": "target_id", "type": "text", "placeholder": "ID Pelanggan PLN", "required": True},
    "customer_id": {"name": "target_id", "type": "text", "placeholder": "Customer ID", "required": True},
    "user_id": {"name": "target_id", "type": "text", "placeholder": "User ID", "required": True},
    "zone_id": {"name": "server_id", "type": "text", "placeholder": "Zone ID / Server ID", "required": True},
    "server_id": {"name": "server_id", "type": "text", "placeholder": "Server ID", "required": True},
}
DEFAULT_LOGO = "https://i.pinimg.com/736x/c7/40/65/c74065540ccade0683a869b622cdc4a6.jpg"

BRAND_LOGOS = {
    # 🟢 Operator Seluler
    "telkomsel": "https://i.pinimg.com/736x/e9/01/3f/e9013f627630a4c7f993efe57de1fc72.jpg",
    "indosat": "https://i.pinimg.com/736x/03/65/e4/0365e4069ad915514e7a3752dc5990ae.jpg",
    "xl": "https://i.pinimg.com/736x/51/12/55/5112554dfb04437fe46e0d811b9496d2.jpg",
    "axis": "https://i.pinimg.com/736x/78/51/97/78519750978af702e07e28d522d3cf3a.jpg",
    "tri": "https://i.pinimg.com/736x/c8/40/87/c84087e787b376b50c42915b00671799.jpg",
    "smartfren": "https://i.pinimg.com/736x/2a/f9/96/2af996bdf8a862ac8567a4ce6316fe1a.jpg",
    "by.u": "https://i.pinimg.com/736x/e8/81/ae/e881ae14dadad14b23835b476865ce41.jpg",

    # 🟢 E-Money
    "dana": "https://i.pinimg.com/736x/f2/7d/e0/f27de0e4a01ba9dfe8607ac03a4f7aae.jpg",
    "ovo": "https://i.pinimg.com/736x/41/25/e1/4125e1126d4042dfd278b30f20482926.jpg",
    "gopay": "https://i.pinimg.com/736x/c7/40/65/c74065540ccade0683a869b622cdc4a6.jpg",
    "shopee pay": "https://i.pinimg.com/736x/9e/6e/51/9e6e51d6b86ff434a4b26102703aee5f.jpg",
    "linkaja": "https://i.ibb.co/5F6gSTf/linkaja.png",

    # 🟢 PLN & Utilitas
    "pln": "https://i.pinimg.com/736x/31/99/26/319926be18194ea0cbaa1c3cac0547f7.jpg",
    "pertamina gas": "https://i.pinimg.com/736x/ef/2a/53/ef2a53eaa734bb060f6d7f442b35cf4f.jpg",
    "k-vision dan gol": "https://i.pinimg.com/736x/0e/e6/b7/0ee6b7d09d50ef1a6120e1c2cb9f9f05.jpg",

    # 🟢 Game Populer
    "mobile legends": "https://i.pinimg.com/736x/90/62/6a/90626a64bfcf430c9ee6b693d1f36426.jpg",
    "free fire": "https://i.pinimg.com/736x/9b/aa/66/9baa66a3fb33bfcea3e8b791dee5d1c7.jpg",
    "pubg mobile": "https://i.pinimg.com/736x/d7/00/35/d700358872ea04fd5639226cd072d148.jpg",
    "genshin impact": "https://i.ibb.co/vwhqL5L/genshin.png",
}
