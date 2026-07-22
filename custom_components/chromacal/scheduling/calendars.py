"""Static regional holiday calendars, ported verbatim from dist/chromacal.html.

Every entry here matches the corresponding {m,d1,d2,name,cat,icon,colors,type}
literal in chromacal.html's US_HOLIDAYS/CA_HOLIDAYS/.../GLOBAL_FLOATING
arrays. Category display metadata (name/desc/icon/color) lives in
custom_components/chromacal/const.py from Phase 1 — it's a config-flow/UI
concern, not something get_enabled_holidays/resolve_tier_winner/
get_night_segments touch, so it isn't duplicated here.
"""

from __future__ import annotations

from .models import HolidayEvent as H

# ── US HOLIDAY CALENDAR (also the default/fallback region) ─────────────────
US_HOLIDAYS: tuple[H, ...] = (
    # ── FEDERAL (all 11 official US federal holidays) ──────────────────────
    H(1, 1, 1, "New Year's Day", "federal", "🎆", ("#DC143C", "#FFD700", "#C0C0C8"), "holiday"),
    H(1, 20, 20, "MLK Day", "federal", "✊", ("#B22222", "#FFD700"), "holiday", "ANNUAL 3rd Mon Jan"),
    H(2, 16, 16, "Presidents' Day", "federal", "🦅", ("#DC143C", "#FFFFFF", "#0032D2"), "holiday", "ANNUAL 3rd Mon Feb"),
    H(5, 25, 25, "Memorial Day", "military", "🇺🇸", ("#DC143C", "#FFFFFF", "#0032D2"), "vigil", "ANNUAL last Mon May"),
    H(6, 14, 14, "Flag Day", "federal", "🚩", ("#DC143C", "#FFFFFF", "#0032D2"), "holiday"),
    H(6, 19, 19, "Juneteenth", "federal", "✊", ("#B22234", "#FFFFFF", "#3C3B6E"), "holiday"),
    H(7, 4, 4, "Independence Day", "federal", "🎇", ("#DC143C", "#FFFFFF", "#0032D2"), "holiday"),
    H(9, 7, 7, "Labor Day", "federal", "⚒️", ("#DC143C", "#FFFFFF", "#0032D2"), "holiday", "ANNUAL 1st Mon Sep"),
    H(10, 12, 12, "Indigenous Peoples Day", "heritage", "🪶", ("#8B2500", "#FFD700", "#228B22"), "holiday", "ANNUAL 2nd Mon Oct"),
    H(11, 11, 11, "Veterans Day", "military", "🎖️", ("#DC143C", "#FFFFFF", "#0032D2"), "holiday"),
    H(11, 26, 26, "Thanksgiving", "federal", "🦃", ("#FF8C00", "#8B4513"), "holiday", "ANNUAL 4th Thu Nov"),
    H(12, 25, 25, "Christmas Day", "federal", "🎄", ("#DC143C", "#00A01E", "#FFFFFF"), "holiday"),
    # ── CULTURAL CELEBRATIONS ───────────────────────────────────────────────
    H(2, 2, 2, "Groundhog Day", "cultural", "🐿️", ("#8B6914", "#DEBA87"), "holiday"),
    H(2, 14, 14, "Valentine's Day", "cultural", "❤️", ("#DC143C", "#FF69B4"), "holiday"),
    H(2, 17, 17, "Mardi Gras / Fat Tuesday", "cultural", "🎭", ("#9400D3", "#00A01E", "#FFD700"), "holiday", "ANNUAL Tue before Ash Wed"),
    H(3, 17, 17, "St. Patrick's Day", "cultural", "🍀", ("#009A00",), "holiday"),
    H(4, 22, 22, "Earth Day", "cultural", "🌍", ("#228B22", "#1E90FF"), "holiday"),
    H(5, 5, 5, "Cinco de Mayo", "cultural", "🎉", ("#006847", "#FFFFFF", "#CE1126"), "holiday"),
    H(5, 10, 10, "Mother's Day", "cultural", "💐", ("#FF69B4", "#FF1493"), "holiday", "ANNUAL 2nd Sun May"),
    H(6, 21, 21, "Father's Day", "cultural", "👨", ("#0064C8", "#1E3A5F"), "holiday", "ANNUAL 3rd Sun Jun"),
    H(10, 31, 31, "Halloween", "cultural", "🎃", ("#FF5000", "#9400D3"), "holiday"),
    H(12, 31, 31, "New Year's Eve", "cultural", "🥂", ("#FFD700", "#C0C0C8", "#FFFFFF"), "holiday"),
    # ── MILITARY & VETERANS ──────────────────────────────────────────────────
    H(3, 29, 29, "Vietnam Veterans Day", "military", "🎗️", ("#DC143C", "#FFFFFF", "#0032D2"), "vigil"),
    H(5, 8, 8, "VE Day", "military", "✌️", ("#DC143C", "#FFFFFF", "#0032D2"), "holiday"),
    H(5, 16, 16, "Armed Forces Day", "military", "⚔️", ("#DC143C", "#FFFFFF", "#0032D2"), "holiday", "ANNUAL 3rd Sat May"),
    H(6, 6, 6, "D-Day Anniversary", "military", "⚓", ("#DC143C", "#FFFFFF", "#0032D2"), "vigil"),
    H(7, 27, 27, "Korean War Veterans Armistice Day", "military", "🕊️", ("#DC143C", "#FFFFFF", "#0032D2"), "vigil"),
    H(8, 4, 4, "Coast Guard Birthday", "military", "⚓", ("#003087", "#FFFFFF", "#CC0000"), "holiday"),
    H(8, 7, 7, "Purple Heart Day", "military", "💜", ("#9400D3", "#FFD700"), "vigil"),
    H(9, 11, 11, "Patriot Day", "military", "🗽", ("#DC143C", "#FFFFFF", "#0032D2"), "vigil"),
    H(9, 19, 19, "POW·MIA Recognition Day", "military", "🕯️", ("#000000", "#FFFFFF"), "vigil", "ANNUAL 3rd Fri Sep"),
    H(9, 18, 18, "Air Force Birthday", "military", "✈️", ("#003087", "#FFFFFF", "#C0C0C8"), "holiday"),
    H(9, 27, 27, "Gold Star Mother's and Family's Day", "military", "⭐", ("#FFD700", "#000000"), "vigil", "ANNUAL last Sun Sep"),
    H(10, 13, 13, "Navy Birthday", "military", "⚓", ("#003087", "#FFFFFF"), "holiday"),
    H(11, 10, 10, "USMC Birthday", "military", "🎂", ("#FF2400", "#FFD700"), "sacred"),
    H(12, 7, 7, "Pearl Harbor Remembrance Day", "military", "🕯️", ("#DC143C", "#FFFFFF", "#0032D2"), "vigil"),
    # ── HERITAGE & CULTURAL MONTHS ───────────────────────────────────────────
    H(2, 1, 28, "Black History Month", "heritage", "✊", ("#DC143C", "#000000", "#009614"), "awareness"),
    H(3, 8, 8, "International Women's Day", "heritage", "♀️", ("#9400D3", "#FFFFFF", "#FFD700"), "holiday"),
    H(3, 1, 31, "Women's History Month", "heritage", "♀️", ("#9400D3", "#FFFFFF", "#FFD700"), "awareness"),
    H(5, 1, 31, "AAPI Heritage + Mental Health Awareness", "heritage", "🎏", ("#DE2910", "#FFDE00", "#00B46E"), "awareness"),
    H(5, 1, 31, "Jewish American Heritage Month", "heritage", "✡️", ("#003CB3", "#FFFFFF", "#FFD700"), "awareness"),
    H(6, 1, 30, "Caribbean American Heritage Month", "heritage", "🌴", ("#009B77", "#FFD700", "#DC143C"), "awareness"),
    # Hispanic Heritage Month spans Sep 15-Oct 15 (stored in two monthly segments)
    H(9, 15, 30, "Suicide Prevention + Hispanic Heritage Month", "heritage", "🌺", ("#9400D3", "#009696", "#DC143C", "#FFFFFF", "#009A3E"), "awareness"),
    H(9, 1, 30, "Suicide Prevention Month", "awareness", "💙", ("#9400D3", "#009696"), "awareness"),
    H(10, 1, 15, "Hispanic Heritage Month (Oct)", "heritage", "🌺", ("#DC143C", "#FFFFFF", "#009A3E"), "awareness"),
    H(10, 1, 31, "Italian American Heritage Month", "heritage", "🍕", ("#009246", "#FFFFFF", "#CE2B37"), "awareness"),
    H(11, 1, 30, "Native American Heritage Month", "heritage", "🪶", ("#8B2500", "#FFD700", "#228B22"), "awareness"),
    # ── PRIDE & LGBTQ+ ───────────────────────────────────────────────────────
    H(6, 1, 30, "Pride Month", "pride", "🏳️‍🌈", ("#FF0000", "#FF7F00", "#FFFF00", "#00C800", "#0032D2", "#9400D3"), "awareness"),
    H(7, 1, 31, "Disability Pride Month", "awareness", "♿", ("#FFFF00", "#FFFFFF", "#A8A8A8", "#0072CE", "#00A650", "#E50000"), "awareness"),
    H(10, 11, 11, "National Coming Out Day", "pride", "🏳️‍🌈", ("#FF7F00", "#FFFFFF"), "holiday"),
    H(11, 20, 20, "Transgender Day of Remembrance", "pride", "🏳️‍⚧️", ("#55CDFC", "#F7A8B8", "#FFFFFF"), "vigil"),
    # ── HEALTH & AWARENESS MONTHS ────────────────────────────────────────────
    H(2, 1, 28, "American Heart Month", "awareness", "❤️", ("#DC143C", "#FF69B4"), "awareness"),
    H(4, 1, 30, "Sexual Assault Awareness + Military Child + Autism Acceptance", "awareness", "💙", ("#009696", "#9400D3", "#0064C8"), "awareness"),
    H(6, 1, 30, "Men's Health Month", "awareness", "💙", ("#0064C8", "#00A01E"), "awareness"),
    H(10, 1, 31, "Breast Cancer + Domestic Violence + Down Syndrome Awareness", "awareness", "🎀", ("#FF69B4", "#9400D3", "#0072CE"), "awareness"),
    H(11, 1, 30, "Movember + Alzheimer's Awareness", "awareness", "💙", ("#0064C8", "#9400D3"), "awareness"),
    H(12, 1, 1, "World AIDS Day", "awareness", "🎗️", ("#DC143C", "#000000"), "holiday"),
    # ── RELIGIOUS OBSERVANCES ────────────────────────────────────────────────
    H(1, 6, 6, "Epiphany / Three Kings' Day", "religious", "⭐", ("#FFD700", "#9400D3", "#DC143C"), "holiday"),
    H(2, 18, 18, "Ash Wednesday", "religious", "✝️", ("#808080", "#4B0082"), "vigil", "ANNUAL 46 days before Easter"),
    H(4, 3, 3, "Good Friday", "religious", "✝️", ("#8B0000", "#4B0082"), "vigil", "ANNUAL Fri before Easter"),
    H(4, 5, 5, "Easter Sunday", "religious", "🐣", ("#FFFD96", "#98FF98", "#FFB6C1", "#C8A2C8"), "holiday", "ANNUAL Apr-May varies"),
    H(12, 1, 24, "Advent / Christmas Season", "religious", "🕯️", ("#DC143C", "#00A01E", "#4B0082"), "awareness"),
    H(12, 24, 24, "Christmas Eve", "religious", "🕯️", ("#DC143C", "#00A01E", "#FFD700"), "holiday"),
    H(12, 26, 30, "Kwanzaa", "heritage", "🕯️", ("#DC143C", "#000000", "#009614"), "holiday"),
)

# ── CANADA ───────────────────────────────────────────────────────────────────
CA_HOLIDAYS: tuple[H, ...] = (
    H(1, 1, 1, "New Year's Day", "federal", "🎆", ("#FF0000", "#FFFFFF"), "holiday"),
    H(2, 14, 14, "Valentine's Day", "cultural", "❤️", ("#FF1493", "#DC143C"), "holiday"),
    H(4, 3, 3, "Good Friday", "religious", "✝️", ("#8B0000",), "holiday", "ANNUAL Fri before Easter"),
    H(5, 19, 19, "Victoria Day", "federal", "👑", ("#FF0000", "#FFFFFF"), "holiday", "ANNUAL 3rd Mon May"),
    H(7, 1, 1, "Canada Day", "federal", "🍁", ("#FF0000", "#FFFFFF"), "holiday"),
    H(9, 1, 1, "Labour Day", "federal", "⚒️", ("#FF0000", "#FFFFFF"), "holiday", "ANNUAL"),
    H(10, 13, 13, "Thanksgiving (Canada)", "federal", "🍂", ("#FF8C00", "#C84600"), "holiday", "ANNUAL 2nd Mon Oct"),
    H(11, 11, 11, "Remembrance Day", "military", "🌹", ("#DC143C",), "vigil"),
    H(12, 25, 25, "Christmas Day", "religious", "🎄", ("#DC143C", "#00A01E"), "holiday"),
    H(12, 26, 26, "Boxing Day", "federal", "📦", ("#FF0000", "#FFFFFF"), "holiday"),
)

# ── UNITED KINGDOM ───────────────────────────────────────────────────────────
UK_HOLIDAYS: tuple[H, ...] = (
    H(1, 1, 1, "New Year's Day", "federal", "🎆", ("#012169", "#FFFFFF", "#C8102E"), "holiday"),
    H(3, 1, 1, "St. David's Day", "heritage", "🏴", ("#00AB39", "#FFFFFF"), "holiday"),
    H(3, 17, 17, "St. Patrick's Day", "heritage", "🍀", ("#009A49",), "holiday"),
    H(4, 3, 3, "Good Friday", "religious", "✝️", ("#8B0000",), "holiday", "ANNUAL Fri before Easter"),
    H(4, 6, 6, "Easter Monday", "religious", "🐣", ("#FFFD96", "#C8A2C8"), "holiday", "ANNUAL Mon after Easter"),
    H(4, 23, 23, "St. George's Day", "heritage", "🏴", ("#FFFFFF", "#C8102E"), "holiday"),
    H(5, 5, 5, "Early May Bank Holiday", "federal", "🌷", ("#012169", "#FFFFFF", "#C8102E"), "holiday", "ANNUAL 1st Mon May"),
    H(5, 26, 26, "Spring Bank Holiday", "federal", "🌸", ("#012169", "#FFFFFF", "#C8102E"), "holiday", "ANNUAL last Mon May"),
    H(8, 25, 25, "Summer Bank Holiday", "federal", "☀️", ("#012169", "#FFFFFF", "#C8102E"), "holiday", "ANNUAL last Mon Aug"),
    H(11, 5, 5, "Bonfire Night", "cultural", "🔥", ("#FF5000", "#FFB81C"), "holiday"),
    H(11, 11, 11, "Remembrance Day", "military", "🌹", ("#DC143C",), "vigil"),
    H(11, 30, 30, "St. Andrew's Day", "heritage", "🏴", ("#005EB8", "#FFFFFF"), "holiday"),
    H(12, 25, 25, "Christmas Day", "religious", "🎄", ("#DC143C", "#00A01E"), "holiday"),
    H(12, 26, 26, "Boxing Day", "federal", "📦", ("#012169", "#FFFFFF", "#C8102E"), "holiday"),
)

# ── AUSTRALIA / NZ ───────────────────────────────────────────────────────────
AU_HOLIDAYS: tuple[H, ...] = (
    H(1, 1, 1, "New Year's Day", "federal", "🎆", ("#00008B", "#FFFFFF", "#FF0000"), "holiday"),
    H(1, 26, 26, "Australia Day", "federal", "🦘", ("#00008B", "#FFFFFF", "#FF0000"), "holiday"),
    H(4, 3, 3, "Good Friday", "religious", "✝️", ("#8B0000",), "holiday", "ANNUAL Fri before Easter"),
    H(4, 4, 4, "Easter Saturday", "religious", "🐣", ("#FFFD96", "#C8A2C8"), "holiday", "ANNUAL Sat before Easter"),
    H(4, 5, 5, "Easter Sunday", "religious", "🐣", ("#FFFD96", "#C8A2C8"), "holiday", "ANNUAL Sunday of Easter"),
    H(4, 6, 6, "Easter Monday", "religious", "🐣", ("#FFFD96", "#C8A2C8"), "holiday", "ANNUAL Mon after Easter"),
    H(4, 25, 25, "ANZAC Day", "military", "🌺", ("#DC143C", "#FFD700"), "vigil"),
    H(6, 9, 9, "King's Birthday", "federal", "👑", ("#00008B", "#FFFFFF", "#FF0000"), "holiday", "ANNUAL varies by state"),
    H(12, 25, 25, "Christmas Day", "religious", "🎄", ("#DC143C", "#00A01E"), "holiday"),
    H(12, 26, 26, "Boxing Day", "federal", "📦", ("#00008B", "#FFFFFF", "#FF0000"), "holiday"),
)

# ── EUROPE ───────────────────────────────────────────────────────────────────
EU_HOLIDAYS: tuple[H, ...] = (
    # ── PAN-EUROPEAN ─────────────────────────────────────────────────────────
    H(1, 1, 1, "New Year's Day", "federal", "🎆", ("#003399", "#FFFFFF", "#FFD700"), "holiday"),
    H(2, 18, 18, "Carnival / Mardi Gras", "cultural", "🎭", ("#9400D3", "#00A01E", "#FFD700"), "holiday", "ANNUAL varies Feb-Mar (Tue before Ash Wed)"),
    H(4, 3, 3, "Good Friday", "religious", "✝️", ("#8B0000", "#4B0082"), "vigil", "ANNUAL varies Apr"),
    H(4, 6, 6, "Easter Monday", "religious", "🐣", ("#FFFD96", "#98FF98", "#C8A2C8"), "holiday", "ANNUAL Mon after Easter"),
    H(5, 1, 1, "Labour Day / May Day", "federal", "⚒️", ("#DC143C", "#FFFFFF"), "holiday"),
    H(5, 8, 8, "VE Day", "federal", "✌️", ("#003399", "#FFD700", "#FFFFFF"), "holiday"),
    H(5, 9, 9, "Europe Day", "federal", "🇪🇺", ("#003399", "#FFD700"), "holiday"),
    H(5, 14, 14, "Ascension Day", "religious", "✝️", ("#FFD700", "#FFFFFF"), "holiday", "ANNUAL 39 days after Easter"),
    H(5, 24, 24, "Pentecost Monday / Whit Monday", "religious", "🕊️", ("#FF0000", "#FFD700"), "holiday", "ANNUAL 50 days after Easter"),
    H(8, 15, 15, "Assumption of Mary", "religious", "✝️", ("#4169E1", "#FFFFFF", "#FFD700"), "holiday"),
    H(11, 1, 1, "All Saints' Day", "religious", "🕯️", ("#FFFFFF", "#C8A2C8"), "holiday"),
    H(12, 8, 8, "Immaculate Conception", "religious", "✝️", ("#4169E1", "#FFFFFF"), "holiday"),
    H(12, 25, 25, "Christmas Day", "religious", "🎄", ("#DC143C", "#00A01E"), "holiday"),
    H(12, 26, 26, "St. Stephen's Day / Boxing Day", "federal", "📦", ("#DC143C", "#00A01E"), "holiday"),
    # ── NATIONAL DAYS ────────────────────────────────────────────────────────
    H(3, 25, 25, "Greek Independence Day", "federal", "🇬🇷", ("#0D5EAF", "#FFFFFF"), "holiday"),
    H(3, 17, 17, "St. Patrick's Day (Ireland)", "heritage", "🍀", ("#009A49", "#FF7900", "#FFFFFF"), "holiday"),
    H(4, 27, 27, "King's Day (Netherlands)", "federal", "👑", ("#FF6600", "#FFFFFF"), "holiday"),
    H(5, 3, 3, "Constitution Day (Poland)", "federal", "🇵🇱", ("#DC143C", "#FFFFFF"), "holiday"),
    H(5, 17, 17, "Constitution Day (Norway)", "federal", "🇳🇴", ("#EF2B2D", "#FFFFFF", "#002868"), "holiday"),
    H(6, 2, 2, "Republic Day (Italy)", "federal", "🇮🇹", ("#009246", "#FFFFFF", "#CE2B37"), "holiday"),
    H(6, 5, 5, "Constitution Day (Denmark)", "federal", "🇩🇰", ("#C60C30", "#FFFFFF"), "holiday"),
    H(6, 6, 6, "National Day (Sweden)", "federal", "🇸🇪", ("#006AA7", "#FECC02"), "holiday"),
    H(6, 10, 10, "Portugal Day", "federal", "🇵🇹", ("#006600", "#FF0000"), "holiday"),
    H(7, 14, 14, "Bastille Day (France)", "federal", "🇫🇷", ("#002395", "#FFFFFF", "#ED2939"), "holiday"),
    H(7, 21, 21, "Belgian National Day", "federal", "🇧🇪", ("#000000", "#FFD100", "#EF3340"), "holiday"),
    H(8, 1, 1, "Swiss National Day", "federal", "🇨🇭", ("#FF0000", "#FFFFFF"), "holiday"),
    H(10, 3, 3, "German Unity Day", "federal", "🇩🇪", ("#000000", "#DD0000", "#FFCE00"), "holiday"),
    H(10, 12, 12, "Spain's National Day", "federal", "🇪🇸", ("#AA151B", "#F1BF00"), "holiday"),
    H(10, 26, 26, "Austrian National Day", "federal", "🇦🇹", ("#ED2939", "#FFFFFF"), "holiday"),
    H(10, 28, 28, "Czech Independence Day", "federal", "🇨🇿", ("#D7141A", "#11457E", "#FFFFFF"), "holiday"),
    H(11, 1, 1, "Portugal/Spain All Saints'", "religious", "✝️", ("#FFFFFF", "#C8A2C8"), "holiday"),
    H(11, 11, 11, "Armistice Day / Polish Independence", "military", "🌹", ("#DC143C", "#FFFFFF", "#DC143C"), "vigil"),
    H(12, 5, 6, "St. Nicholas Day", "cultural", "🎅", ("#DC143C", "#FFD700", "#FFFFFF"), "holiday"),
    H(12, 6, 6, "Finnish Independence Day", "federal", "🇫🇮", ("#003580", "#FFFFFF"), "holiday"),
)

# ── ASIA-PACIFIC ─────────────────────────────────────────────────────────────
APAC_HOLIDAYS: tuple[H, ...] = (
    H(1, 1, 1, "New Year's Day", "federal", "🎆", ("#FF0000", "#FFFFFF"), "holiday"),
    H(1, 28, 31, "Lunar New Year", "cultural", "🧧", ("#FF0000", "#FFD700"), "holiday", "ANNUAL late Jan/Feb"),
    H(2, 6, 6, "Waitangi Day (NZ)", "federal", "🇳🇿", ("#00247D", "#FFFFFF", "#CC142B"), "holiday"),
    H(2, 11, 11, "National Foundation Day (JP)", "federal", "🇯🇵", ("#BC002D", "#FFFFFF"), "holiday"),
    H(4, 25, 25, "ANZAC Day (AU/NZ)", "military", "🌺", ("#DC143C", "#FFD700"), "vigil"),
    H(5, 3, 5, "Golden Week (Japan)", "cultural", "🎏", ("#BC002D", "#FFFFFF"), "holiday"),
    H(8, 9, 9, "National Day (Singapore)", "federal", "🇸🇬", ("#EF3340", "#FFFFFF"), "holiday"),
    H(8, 15, 15, "Liberation Day (Korea)", "federal", "🇰🇷", ("#003478", "#FFFFFF", "#CD2E3A"), "holiday"),
    H(10, 1, 1, "National Day (China)", "federal", "🇨🇳", ("#DE2910", "#FFD700"), "holiday"),
    H(10, 3, 3, "National Foundation Day (KR)", "federal", "🇰🇷", ("#003478", "#FFFFFF", "#CD2E3A"), "holiday"),
    H(11, 3, 3, "Culture Day (Japan)", "cultural", "🎌", ("#BC002D", "#FFFFFF"), "holiday"),
    H(12, 25, 25, "Christmas Day", "religious", "🎄", ("#DC143C", "#00A01E"), "holiday"),
)

# ── LATIN AMERICA ────────────────────────────────────────────────────────────
LATAM_HOLIDAYS: tuple[H, ...] = (
    H(1, 1, 1, "New Year's Day", "federal", "🎆", ("#006847", "#FFFFFF", "#CE1126"), "holiday"),
    H(2, 5, 5, "Constitution Day (Mexico)", "federal", "🇲🇽", ("#006847", "#FFFFFF", "#CE1126"), "holiday", "ANNUAL 1st Mon Feb"),
    H(3, 21, 21, "Benito Juárez Birthday", "federal", "🇲🇽", ("#006847", "#FFFFFF", "#CE1126"), "holiday", "ANNUAL 3rd Mon Mar"),
    H(4, 18, 18, "Holy Thursday", "religious", "✝️", ("#8B0000",), "holiday", "ANNUAL"),
    H(4, 3, 3, "Good Friday", "religious", "✝️", ("#8B0000",), "holiday", "ANNUAL Fri before Easter"),
    H(5, 1, 1, "Labour Day", "federal", "⚒️", ("#DC143C", "#FFFFFF"), "holiday"),
    H(9, 15, 16, "Mexican Independence Day", "federal", "🇲🇽", ("#006847", "#FFFFFF", "#CE1126"), "holiday"),
    H(11, 1, 2, "Día de Muertos", "cultural", "💀", ("#FF5000", "#FFB81C", "#9400D3"), "holiday"),
    H(11, 18, 18, "Revolution Day (Mexico)", "federal", "🇲🇽", ("#006847", "#FFFFFF", "#CE1126"), "holiday", "ANNUAL 3rd Mon Nov"),
    H(12, 12, 12, "Our Lady of Guadalupe", "religious", "🙏", ("#006847", "#FFFFFF", "#CE1126"), "holiday"),
    H(12, 25, 25, "Christmas Day", "religious", "🎄", ("#DC143C", "#00A01E"), "holiday"),
)

# ── GLOBAL FLOATING (approximate — the real fix for these is Phase v2-calendar-sync) ─
GLOBAL_FLOATING: tuple[H, ...] = (
    H(1, 29, 31, "Lunar New Year", "cultural", "🧧", ("#FF0000", "#FFD700"), "holiday", "ANNUAL late Jan/early Feb"),
    H(3, 30, 30, "Eid al-Fitr", "religious", "🌙", ("#00563F", "#FFD700", "#FFFFFF"), "holiday", "ANNUAL varies (Islamic calendar)"),
    H(4, 1, 30, "Ramadan (final days)", "religious", "🌙", ("#00563F", "#FFD700"), "awareness", "ANNUAL 30-day fast, dates vary"),
    H(6, 6, 7, "Eid al-Adha", "religious", "🌙", ("#00563F", "#FFD700", "#FFFFFF"), "holiday", "ANNUAL varies (Islamic calendar)"),
    H(9, 22, 22, "Rosh Hashanah", "religious", "✡️", ("#003CB3", "#FFFFFF", "#FFD700"), "holiday", "ANNUAL varies Sep-Oct"),
    H(10, 1, 1, "Yom Kippur", "religious", "✡️", ("#003CB3", "#FFFFFF"), "vigil", "ANNUAL 10 days after Rosh Hashanah"),
    H(10, 6, 13, "Sukkot", "religious", "✡️", ("#003CB3", "#FFD700", "#00A01E"), "awareness", "ANNUAL 7-day festival after Yom Kippur"),
    H(4, 13, 20, "Passover (Pesach)", "religious", "✡️", ("#003CB3", "#FFFFFF", "#FFD700"), "awareness", "ANNUAL 8 days, varies Apr"),
    H(10, 20, 26, "Diwali", "religious", "🪔", ("#FF8C00", "#FFD700", "#FF5000"), "holiday", "ANNUAL Oct-Nov varies"),
    H(12, 4, 12, "Hanukkah", "religious", "🕎", ("#003CB3", "#FFFFFF", "#C0C0C8"), "awareness", "ANNUAL Nov-Dec varies (8 nights)"),
    # Pagan/Wiccan cross-quarter days -- fixed dates, always standard (single-evening) treatment.
    H(2, 1, 1, "Imbolc", "pagan", "🕯️", ("#FFFFFF", "#8FBC8F"), "holiday", "ANNUAL Feb 1 — Brigid's flame, purification, first stirrings of spring"),
    H(5, 1, 1, "Beltane", "pagan", "🔥", ("#E63946", "#52B788", "#FFB5C5"), "holiday", "ANNUAL May 1 — fire festival, fertility, the bright half of the year"),
    H(8, 1, 1, "Lughnasadh", "pagan", "🌾", ("#D4A017", "#8B5A2B"), "holiday", "ANNUAL Aug 1 — first harvest, grain, gratitude"),
    H(10, 31, 31, "Samhain", "pagan", "🍂", ("#1A1A1A", "#FF7518", "#4B0082"), "holiday", "ANNUAL Oct 31 — end of harvest, ancestor veneration, the veil thins"),
)

# region key -> calendar. "us" maps to None in v1 (falls back to US_HOLIDAYS) —
# kept identical here so get_enabled_holidays' fallback logic matches exactly.
REGION_CALENDARS: dict[str, tuple[H, ...] | None] = {
    "us": None,
    "ca": CA_HOLIDAYS,
    "uk": UK_HOLIDAYS,
    "au": AU_HOLIDAYS,
    "eu": EU_HOLIDAYS,
    "apac": APAC_HOLIDAYS,
    "latam": LATAM_HOLIDAYS,
    "global": GLOBAL_FLOATING,
}
