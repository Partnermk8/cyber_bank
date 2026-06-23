import random
import flet as ft
import json
import os

SAVE_FILE = "cyber_bank_save.json"


def main(page: ft.Page):
    # ПРЕДОХРАНИТЕЛЬ ДЛЯ GITHUB PAGES:
    # Защита от вылета при попытке изменить размер окна в браузере
    page.web = page.web if hasattr(page, 'web') else (page.client_ip is not None)

    page.title = "Коммерсант 2026: Квантовый Синдикат"

    if not page.web:
        try:
            page.window.width = 470
            page.window.height = 880
        except:
            page.window_width = 470
            page.window_height = 880

    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#121418"
    page.scroll = ft.ScrollMode.ALWAYS

    shortcuts = {
        "Нефть": "Н", "Газ": "Г", "Цифровой Доллар": "Д",
        "Золото": "З",
        "Нейросети": "НС", "Био-Чипы": "БЧ", "Квантовые Ядра": "КЯ", "Темная Материя": "ТМ"
    }

    default_state = {
        "money": 10000, "turn": 1, "level": 1, "goal": 250000,
        "is_blackmailed": False, "mafia_active": False,
        "bots_count": 0, "has_lawyer": False, "loan": 0,
        "mafia_demand": 5000, "mafia_text": "Криминальный синдикат заблокировал твои счета.",
        "last_tax_day": -100,
        "last_mafia_day": -100,
        "last_lottery_day": -200,
        "last_good_event_day": -40,
        "last_bad_event_day": -40,
        "last_global_crisis_day": -150,
        "assets": {"Нефть": 0, "Газ": 0, "Цифровой Доллар": 0, "Золото": 0},
        "prices": {"Нефть": 50, "Газ": 20, "Цифровой Доллар": 100, "Золото": 500},
        "previous_prices": {"Нефть": 50, "Газ": 20, "Цифровой Доллар": 100, "Золото": 500},
        "trends": {"Нефть": ["-", "-", "-"], "Цифровой Доллар": ["-", "-", "-"], "Газ": ["-", "-", "-"],
                   "Золото": ["-", "-", "-"]}
    }

    state = {}

    def save_game():
        # В браузере сохранение в файл работать не будет, поэтому оборачиваем в try
        try:
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=4)
        except Exception as ex:
            pass  # Ошибки сохранения в вебе игнорируются

    def load_game():
        nonlocal state
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r", encoding="utf-8") as f:
                    state = json.load(f)
                for asset in state["prices"]:
                    if asset not in state["trends"]:
                        state["trends"][asset] = ["-", "-", "-"]
                keys_to_check = ["last_tax_day", "last_mafia_day", "last_lottery_day", "last_good_event_day",
                                 "last_bad_event_day", "last_global_crisis_day"]
                for k in keys_to_check:
                    if k not in state: state[k] = -200
                return True
            except:
                state = json.loads(json.dumps(default_state))
                return False
        else:
            state = json.loads(json.dumps(default_state))
            return False

    is_loaded = load_game()

    def get_total_capital():
        return state["money"] + sum(state["assets"].get(k, 0) * state["prices"].get(k, 0) for k in state["assets"]) - \
            state["loan"]

    def make_btn(text, on_click, bg="#252830", color="#4ABFFF", width=None, height=38):
        return ft.Container(
            content=ft.Row(
                controls=[ft.Text(text, color=color, weight="bold", size=12, text_align=ft.TextAlign.CENTER)],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            bgcolor=bg,
            padding=8,
            border_radius=6,
            on_click=on_click,
            width=width,
            height=height
        )

    def reset_game_click(e):
        nonlocal state
        if os.path.exists(SAVE_FILE):
            try:
                os.remove(SAVE_FILE)
            except:
                pass
        state = json.loads(json.dumps(default_state))
        log_column.controls.clear()
        log_message("Система перезагружена. Начата новая симуляция.", "#4ABFFF")
        update_ui()

    def level_up_click(e):
        if state["level"] == 1:
            state["level"] = 2
            state["goal"] = 1000000
            for asset, price in [("Нейросети", 1500), ("Био-Чипы", 6000)]:
                state["assets"][asset] = 0
                state["prices"][asset] = price
                state["previous_prices"][asset] = price
                state["trends"][asset] = ["-", "-", "-"]
            log_message(" УРОВЕНЬ 2: Открыт мировой рынок хай-тека! Цель: 1,000,000$", "#4AFF4A")
        elif state["level"] == 2:
            state["level"] = 3
            state["goal"] = 5000000
            for asset, price in [("Квантовые Ядра", 20000), ("Темная Материя", 80000)]:
                state["assets"][asset] = 0
                state["prices"][asset] = price
                state["previous_prices"][asset] = price
                state["trends"][asset] = ["-", "-", "-"]
            log_message(" УРОВЕНЬ 3: Квантовый Синдикат активирован! Цель: 5,000,000$", "#4ABFFF")
        level_banner.visible = False
        update_ui()

    def borrow_click(e):
        state["money"] += 10000
        state["loan"] += 10000
        log_message("Кредит: Получено +10,000$. Начисляется 5% в день.", "#FFB04A")
        update_ui()

    def repay_click(e):
        if state["loan"] <= 0:
            log_message("У вас нет активных задолженностей.", "#707580")
            return
        payment = min(10000, state["loan"])
        if state["money"] >= payment:
            state["loan"] -= payment
            state["money"] -= payment
            log_message(f"Кредит: Погашено {payment}$. Остаток долга: {state['loan']}$", "#4AFF4A")
            update_ui()
        else:
            log_message("Недостаточно наличных для погашения кредита!", "#FF4A4A")

    def buy_bot_click(e):
        if state["money"] >= 25000:
            state["money"] -= 25000
            state["bots_count"] += 1
            log_message(f"Куплен бот (#{state['bots_count']}). Пассив: +1,500$/день", "#4AFF4A")
            update_ui()
        else:
            log_message("Не хватает наличных для покупки Бота (Нужно 25к)!", "#FF4A4A")

    def buy_lawyer_click(e):
        if state["money"] >= 50000 and not state["has_lawyer"]:
            state["money"] -= 50000
            state["has_lawyer"] = True
            log_message("Нанят Кибер-Адвокат! Полная защита от ФНС и -50% налог мафии.", "#4AFF4A")
            update_ui()
        else:
            log_message("Недостаточно средств или контракт уже подписан.", "#FF4A4A")

    def pay_ransom_click(e):
        demand = state["mafia_demand"]
        if state["money"] >= demand:
            state["money"] -= demand
            log_message(f"Вы выплатили {demand:,}$ и урегулировали конфликт.", "#4AFF4A")
            state["mafia_active"] = False
            update_ui()
        else:
            state["is_blackmailed"] = True
            log_message("Наличных не хватило! Синдикат поставил вас на процент.", "#FF4A4A")
            state["mafia_active"] = False
            update_ui()

    def refuse_ransom_click(e):
        state["is_blackmailed"] = True
        log_message("Вы послали мафию. Синдикат начал удаленный арест активов!", "#FF4A4A")
        state["mafia_active"] = False
        update_ui()

    def next_turn_click(e):
        if state["mafia_active"]: return
        state["previous_prices"] = state["prices"].copy()
        state["turn"] += 1
        current_day = state["turn"]

        if state["loan"] > 0:
            interest = int(state["loan"] * 0.05)
            state["loan"] += interest
            log_message(f"Кредит: Начислен ежедневный процент +{interest}$", "#FF4A4A")

        if state["bots_count"] > 0:
            income = state["bots_count"] * 1500
            state["money"] += income
            log_message(f"Инфраструктура: Боты сгенерировали +{income}$", "#4AFF4A")

        max_change = 0.32 if state["level"] == 3 else 0.16
        for asset in list(state["prices"].keys()):
            old_p = state["prices"][asset]
            change = random.uniform(-0.14, max_change)
            state["prices"][asset] = max(5, int(old_p * (1 + change)))
            new_p = state["prices"][asset]
            if new_p > old_p:
                trend_icon = "▲"
            elif new_p < old_p:
                trend_icon = "▼"
            else:
                trend_icon = "▬"

            if asset not in state["trends"]: state["trends"][asset] = ["-", "-", "-"]
            state["trends"][asset].append(trend_icon)
            if len(state["trends"][asset]) > 3: state["trends"][asset].pop(0)

        total_capital = get_total_capital()

        if state["is_blackmailed"]:
            tax_rate = 0.07 if state["level"] >= 2 else 0.04
            if state["has_lawyer"]: tax_rate /= 2
            tax = int(total_capital * tax_rate)
            state["money"] -= tax
            log_message(f"! ШАНТАЖ: Изъято синдикатом {tax}$", "#FF4A4A")

        if current_day % 365 == 0:
            state["money"] += 10000
            log_message("ДЕНЬ РОЖДЕНИЯ: Партнеры по бизнесу прислали подарок: +10,000$!", "#4AFF4A")
            update_ui()
            return

        if random.random() < 0.75:
            generate_event(total_capital, current_day)

        update_ui()

    def generate_event(total_capital, current_day):
        if (current_day - state["last_global_crisis_day"]) >= 150 and random.random() < 0.12:
            state["last_global_crisis_day"] = current_day
            global_crises = [
                {"t": "КАТАСТРОФА: Извержение супервулкана парализовало логистику! Нефть +80%, Цифровой Доллар -50%.",
                 "effects": [("Нефть", 1.8), ("Цифровой Доллар", 0.5)]},
                {"t": "ГЕОШТОРМ: Вспышка на Солнце выжгла спутники. Нейросети и Био-Чипы -60%! Золото +70%.",
                 "effects": [("Нейросети", 0.4), ("Био-Чипы", 0.4), ("Золото", 1.7)]},
                {
                    "t": "ГЕОПОЛИТИКА: Раздел Антарктиды привел к ультиматуму ядерных держав. Нефть и Газ взлетели на +75%!",
                    "effects": [("Нефть", 1.75), ("Газ", 1.75)]},
                {"t": "ЧЕРНЫЙ ПОНЕДЕЛЬНИК: Крах азиатского инвест-фонда. Цифровой Доллар -40%, Золото +60%.",
                 "effects": [("Цифровой Доллар", 0.6), ("Золото", 1.6)]},
                {
                    "t": "КВАНТОВЫЙ КРИЗИС: Ошибка в ядре Синдиката вызвала коллапс. Квантовые Ядра и Темная Материя -70%.",
                    "effects": [("Квантовые Ядра", 0.3), ("Темная Материя", 0.3)]}
            ]
            crisis = random.choice(global_crises)
            for asset, mult in crisis["effects"]:
                if asset in state["prices"]: state["prices"][asset] = int(state["prices"][asset] * mult)
            log_message(crisis["t"], "#FFB04A")
            return

        if (current_day - state["last_lottery_day"]) >= 200 and random.random() < 0.10:
            state["last_lottery_day"] = current_day
            win_money = max(3000, int(total_capital * 0.33))
            state["money"] += win_money
            log_message(f"ВЕЗЕНИЕ: Забытый билет «Нео-Миллион» принес выигрыш (33% капитала): +{win_money:,}$!",
                        "#4AFF4A")
            return

        if total_capital < 100000 and (current_day - state["last_tax_day"]) >= 100 and random.random() < 0.25:
            state["last_tax_day"] = current_day
            tax_penalty = random.randint(2000, 7000)
            if state["has_lawyer"]:
                log_message("НАЛОГОВАЯ: Кибер-Адвокат аннулировал аудит ФНС!", "#4AFF4A")
            else:
                state["money"] -= tax_penalty
                log_message(f"ФНС: Проверка выявила нарушения. Штраф из наличных: -{tax_penalty:,}$", "#FF4A4A")
            return

        if total_capital >= 10000 and (current_day - state["last_mafia_day"]) >= 100 and not state[
            "is_blackmailed"] and not state["mafia_active"] and random.random() < 0.30:
            state["last_mafia_day"] = current_day
            state["mafia_demand"] = max(15000, int(total_capital * 0.25))
            mafia_stories = [
                "Синдикат взломал твой нейрочип. Требуют выкуп за личную память!",
                "Твою умную яхту угнали. Гангстеры вышли на связь.",
                "Хакеры Триады заблокировали серверы твоей компании. Требуют долю.",
                "Твой личный ИИ-ассистент взломан и сливает компромат.",
                "Теневые коллекторы зажали тебя в переулке Нео-Токио."
            ]
            state["mafia_text"] = random.choice(mafia_stories)
            state["mafia_active"] = True
            log_message(f"КРИМИНАЛ: {state['mafia_text']}", "#FF4A4A")
            return

        if random.random() < 0.45:
            if random.random() < 0.50:
                small_good = [
                    {"t": "💬 Слухи: Инсайдеры шепчутся об открытии новых скважин. Нефть +5%.", "tgt": "Нефть",
                     "mult": 1.05, "m": 0},
                    {"t": "💬 Чат трейдеров: Блогер-миллионник закупает Газ. Цена +4%.", "tgt": "Газ", "mult": 1.04,
                     "m": 0},
                    {"t": "💬 Новости рынка: Ожидается легкое ускорение транзакций. Цифровой Доллар +3%.",
                     "tgt": "Цифровой Доллар", "mult": 1.03, "m": 0},
                    {"t": "💬 Форум ювелиров: Спрос на обручальные кольца вырос. Золото +2%.", "tgt": "Золото",
                     "mult": 1.02, "m": 0},
                    {"t": "💬 GitHub: Опубликована микро-оптимизация для кода ИИ. Нейросети +6%.", "tgt": "Нейросети",
                     "mult": 1.06, "m": 0},
                    {"t": "💬 Утечка: Новое поколение фитнес-браслетов получит свежие Био-Чипы. Цена +5%.",
                     "tgt": "Био-Чипы", "mult": 1.05, "m": 0},
                    {"t": "💬 Спекуляции: Фирма-оболочка импортировала Квантовые Ядра. Курс +4%.",
                     "tgt": "Квантовые Ядра", "mult": 1.04, "m": 0},
                    {"t": "💬 DarkNet: Ходят слухи об успешном синтезе стабильной Темной Материи. Цена +7%.",
                     "tgt": "Темная Материя", "mult": 1.07, "m": 0},
                    {"t": "Находка: Продал на аукционе старый раритетный кибер-девайс: +300$.", "tgt": None,
                     "mult": 1.0, "m": 300},
                    {"t": "Экономия: Твой ИИ поменял тариф провайдера. Сэкономлено +150$.", "tgt": None, "mult": 1.0,
                     "m": 150}
                ]
                evt = random.choice(small_good)
                state["money"] += evt["m"]
                if evt["tgt"] and evt["tgt"] in state["prices"]:
                    state["prices"][evt["tgt"]] = int(state["prices"][evt["tgt"]] * evt["mult"])
                log_message(evt["t"], "#707580")
            else:
                small_bad = [
                    {"t": "💬 Слухи: Небольшая забастовка на одном блендере. Нефть -4%.", "tgt": "Нефть", "mult": 0.96,
                     "m": 0},
                    {"t": "💬 Чат трейдеров: Газопровод встал на плановую проверку на день. Газ -3%.", "tgt": "Газ",
                     "mult": 0.97, "m": 0},
                    {"t": "💬 Техсбой: Мелкие задержки в обновлении кошельков. Цифровой Доллар -2%.",
                     "tgt": "Цифровой Доллар", "mult": 0.98, "m": 0},
                    {"t": "💬 Сплетни: Богачи переходят на платиновые украшения. Золото -3%.", "tgt": "Золото",
                     "mult": 0.97, "m": 0},
                    {"t": "💬 Баг-трекер: В открытом коде ИИ нашли мелкую уязвимость. Нейросети -5%.",
                     "tgt": "Нейросети", "mult": 0.95, "m": 0},
                    {"t": "💬 Жалобы: Пользователи жалуются на перегрев свежих Био-Чипов. Цена -4%.", "tgt": "Био-Чипы",
                     "mult": 0.96, "m": 0},
                    {"t": "💬 Домыслы: Эксперт считает Квантовые Ядра переоцененными. Курс -4%.",
                     "tgt": "Квантовые Ядра", "mult": 0.96, "m": 0},
                    {"t": "💬 Слухи: Обнаружена микро-утечка на складе Темной Материи. Цена -6%.",
                     "tgt": "Темная Материя", "mult": 0.94, "m": 0},
                    {"t": "💬 Издержки: Купил подписку на антивирус для торгового терминала: -200$.", "tgt": None,
                     "mult": 1.0, "m": -200},
                    {"t": "💬 Штраф: Небольшое нарушение правил парковки дрона: -150$.", "tgt": None, "mult": 1.0,
                     "m": -150}
                ]
                evt = random.choice(small_bad)
                state["money"] += evt["m"]
                if evt["tgt"] and evt["tgt"] in state["prices"]:
                    state["prices"][evt["tgt"]] = int(state["prices"][evt["tgt"]] * evt["mult"])
                log_message(evt["t"], "#707580")
            return

        if random.random() < 0.50:
            good_events = [
                {"t": "🏛 ФРС: Заседание ФРС объявило о снижении ключевой ставки. Цифровой Доллар укрепился на +20%.",
                 "m": 0, "tgt": "Цифровой Доллар", "mult": 1.20},
                {"t": "🤝 ДИПЛОМАТИЯ: Подписан пакт о ненападении в Персидском заливе. Рынок Нефти: +15%.", "m": 0,
                 "tgt": "Нефть", "mult": 1.15},
                {"t": "📈 ИНТЕГРАЦИЯ: ВТО признала Цифровой Доллар единым платежным средством метаверсов: +25%.", "m": 0,
                 "tgt": "Цифровой Доллар", "mult": 1.25},
                {
                    "t": "📜 СУБСИДИИ ФРС: Глава ФРС выделил триллионный грант на полупроводники. Био-Чипы выросли на +30%.",
                    "m": 0, "tgt": "Био-Чипы", "mult": 1.30},
                {"t": "🌍 ЕВРОСОЮЗ: Сняты пошлины на импортный сжиженный Газ. Цена Газа выросла на +20%.", "m": 0,
                 "tgt": "Газ", "mult": 1.20},
                {"t": "🚀 КОСМОС: ООН одобрила коммерческую добычу на Луне. Котировки Золота выросли на +25%.", "m": 0,
                 "tgt": "Золото", "mult": 1.25},
                {"t": "📜 ЛЕГАЛИЗАЦИЯ: Китай снял запрет на децентрализованные Квантовые Сети. Квантовые Ядра: +35%.",
                 "m": 0, "tgt": "Квантовые Ядра", "mult": 1.35},
                {"t": "🌍 САММИТ G20: Лидеры стран договорились не облагать налогом доходы от ИИ. Нейросети: +25%.",
                 "m": 0, "tgt": "Нейросети", "mult": 1.25},
                {"t": "⚡ ЭНЕРГОПАКТ: Альянс стран заключил соглашение о квотах на чистую энергию. Газ вырос на +15%.",
                 "m": 0, "tgt": "Газ", "mult": 1.15},
                {"t": "⚖️ РЕФОРМА ФРС: ФРС легализовала стейкинг корпоративных облигаций. Бонус наличными +4,000$.",
                 "m": 4000, "tgt": None},
                {"t": "🤖 ПРОРЫВ: OpenAI представила модель GPT-8. Акции Нейросетей подскочили на +35%.", "m": 0,
                 "tgt": "Нейросети", "mult": 1.35},
                {"t": "🧬 БИОТЕХ: Успешно клонированы первые кибернетические органы. Био-Чипы выросли на +30%.", "m": 0,
                 "tgt": "Био-Чипы", "mult": 1.30},
                {"t": "🔬 ФИЗИКА: Ученые стабилизировали поток энергии из Темной Материи. Она подорожала на +40%.",
                 "m": 0, "tgt": "Темная Материя", "mult": 1.40},
                {
                    "t": "🔋 СВЕРХПРОВОДНИК: Синтезирован сверхпроводник при комнатной температуре. Все хай-тек активы +15%.",
                    "m": 0, "tgt": "all_up", "mult": 1.15},
                {"t": "🎁 Кэшбэк от банка: Твой банк обновил систему лояльности. На счет вернулось +1,500$.", "m": 1500,
                 "tgt": None},
                {"t": "🔋 Энергоэффективность: Твой ИИ оптимизировал энергопотребление ферм. Бонус +2,000$.", "m": 2000,
                 "tgt": None},
                {"t": "🧰 Старый долг: Бывший партнер вернул давний долг в крипто-валюте: +3,500$.", "m": 3500,
                 "tgt": None},
                {"t": "💿 Продажа софта: Твой старый скрипт автоторговли купили на форуме за +4,000$.", "m": 4000,
                 "tgt": None},
                {"t": "🤖 Сбой ИИ-налоговой: Робот ФНС ошибся и случайно перевел тебе вычет: +5,000$.", "m": 5000,
                 "tgt": None},
                {"t": "🔌 Грант на инновации: Минцифры выдало субсидию кибер-предпринимателю: +6,000$.", "m": 6000,
                 "tgt": None},
                {"t": "📉 Инсайдерский слив: Знакомый хакер подкинул инсайд. Цены на Газ растут на +20%.", "m": 0,
                 "tgt": "Газ", "mult": 1.20},
                {"t": "🌟 Вирусный твит: Илон Маск опубликовал мем с золотым слитком. Золото выросло на +15%.", "m": 0,
                 "tgt": "Золото", "mult": 1.15},
                {"t": "🐳 Памп рынка: Крупный крипто-кит начал скупать Нефть. Котировки выросли на +25%.", "m": 0,
                 "tgt": "Нефть", "mult": 1.25},
                {"t": "💾 Находка на флешке: На старом накопителе найдены забытые токены: +4,500$.", "m": 4500,
                 "tgt": None},
                {"t": "🛠 Бесплатный апгрейд: Провайдер бесплатно обновил твоих ботов: +3,000$.", "m": 3000,
                 "tgt": None},
                {"t": "📦 Контрабанда: Орбитальный челнок сбросил ящики с Газом. Газ растет на +30%.", "m": 0,
                 "tgt": "Газ", "mult": 1.30},
                {"t": "📜 Компенсация: Суд обязал конкурентов выплатить тебе за спам-атаку: +5,500$.", "m": 5500,
                 "tgt": None},
                {"t": "💎 Юбилейный токен: Ты стал круглым пользователем криптобиржи. Приз: +2,500$.", "m": 2500,
                 "tgt": None},
                {"t": "📈 Удачный шорт: Бот успел сыграть на падении котировок конкурентов: +4,000$.", "m": 4000,
                 "tgt": None},
                {"t": "🤝 Донат: Твой личный экономический блог поддержал крупный меценат: +3,000$.", "m": 3000,
                 "tgt": None}
            ]
            evt = random.choice(good_events)
            state["money"] += evt["m"]
            if evt["tgt"] == "all_up":
                for k in state["prices"]: state["prices"][k] = int(state["prices"][k] * evt["mult"])
            elif evt["tgt"] and evt["tgt"] in state["prices"]:
                state["prices"][evt["tgt"]] = int(state["prices"][evt["tgt"]] * evt["mult"])
            log_message(evt["t"], "#4AFF4A")
        else:
            bad_events = [
                {
                    "t": "💥 ВОЙНА: Вспыхнул вооруженный конфликт в Южно-Китайском море. Поставки Био-Чипов заблокированы: -40%.",
                    "m": 0, "tgt": "Био-Чипы", "mult": 0.60},
                {"t": "🏛 ФРС РЕШЕНИЕ: ФРС резко подняла ставку для борьбы с гиперинфляцией. Рынки упали на -15%.",
                 "m": 0, "tgt": "all_down", "mult": 0.85},
                {"t": "⛔ САНКЦИИ: ООН ввела жесткое эмбарго на экспорт Темной Материи. Цена упала на -35%.", "m": 0,
                 "tgt": "Темная Материя", "mult": 0.65},
                {"t": "🔥 ДИВЕРСИЯ: Взорван магистральный трансатлантический газопровод. Газ рухнул на -30%.", "m": 0,
                 "tgt": "Газ", "mult": 0.70},
                {"t": "⚔ КИБЕР-ВОЙНА: Хакеры Пентагона атаковали ИИ-серверы Азии. Нейросети просели на -25%.", "m": 0,
                 "tgt": "Нейросети", "mult": 0.75},
                {"t": "📜 НАЦИОНАЛИЗАЦИЯ: Правительство конфисковало частные золотые рудники. Золото упало на -20%.",
                 "m": 0, "tgt": "Золото", "mult": 0.80},
                {"t": "📉 КРАХ ФАТФ: Международный регулятор признал Цифровой Доллар временно токсичным: -30%.", "m": 0,
                 "tgt": "Цифровой Доллар", "mult": 0.70},
                {"t": "🛡 БЛОКАДА: Тайвань полностью прекратил отгрузку Квантовых Ядер. Цена просела на -35%.", "m": 0,
                 "tgt": "Квантовые Ядра", "mult": 0.65},
                {"t": "🛑 ЗАКОНОПРОЕКТ ФРС: Новое постановление ФРС ограничивает оборот токенов. Убыток -4,500$.",
                 "m": -4500, "tgt": None},
                {"t": "🌍 ЭКО-МАНИФЕСТ: Конференция по климату ввела огромный налог на добычу Нефти. Цена -20%.", "m": 0,
                 "tgt": "Нефть", "mult": 0.80},
                {"t": "🦠 ВИРУС 'WannaCry-2026': Глобальный вирус парализовал 15% мировых ЦОД. Нейросети упали на -30%.",
                 "m": 0, "tgt": "Нейросети", "mult": 0.70},
                {"t": "💻 ХАКЕРЫ: Произошел массовый взлом кошельков биржи. Цифровой Доллар просел на -20%.", "m": 0,
                 "tgt": "Цифровой Доллар", "mult": 0.80},
                {"t": "⚡ Скачок напряжения: В твоем районе сгорел силовой узел. Замена оборудования: -2,000$.",
                 "m": -2000, "tgt": None},
                {"t": "💸 Фишинг-атака: Ты кликнул на фейковое письмо. Списано хакерами: -1,500$.", "m": -1500,
                 "tgt": None},
                {"t": "🛰 Сбой спутника: Связь упала. Котировки Золота заблокированы и упали на -15%.", "m": 0,
                 "tgt": "Золото", "mult": 0.85},
                {"t": "🦠 Компьютерный червь: Торговые терминалы заражены. Срочная очистка систем: -3,000$.", "m": -3000,
                 "tgt": None},
                {"t": "🛢 Утечка топлива: На арендованном складе прорвало трубу. Эко-штраф: -4,500$.", "m": -4500,
                 "tgt": None},
                {"t": "🛑 Заморозка: Банк заморозил перевод. Комиссия за аудит документов: -2,500$.", "m": -2500,
                 "tgt": None},
                {"t": "🤖 Бунт ботов: Твой ИИ сошел с ума и совершил убыточную сделку: -4,000$.", "m": -4000,
                 "tgt": None},
                {"t": "🕶 Слив данных: База данных твоих транзакций слита. Затраты на защиту: -5,000$.", "m": -5000,
                 "tgt": None},
                {"t": "📦 Таможня: Введены пошлины на ввоз серверных запчастей. Списано: -2,000$.", "m": -2000,
                 "tgt": None},
                {"t": "📱 Поломка: Твой флагманский нейро девайс упал в воду. Покупка нового: -1,800$.", "m": -1800,
                 "tgt": None},
                {"t": "🧰 Издержки: Старый спор по авторским правам потребовал пошлин: -3,000$.", "m": -3000,
                 "tgt": None},
                {"t": "📉 Демпинг: Конкуренты сбрасывают Нефть. Твоя Нефть обесценилась на -20%.", "m": 0,
                 "tgt": "Нефть", "mult": 0.80},
                {"t": "🦹 Карманник: В маглеве у тебя бесконтактно скопировали кошелек: -1,200$.", "m": -1200,
                 "tgt": None},
                {"t": "🏢 Налог на роскошь: ФНС прислала счет за аренду суперкомпьютера: -3,800$.", "m": -3800,
                 "tgt": None},
                {"t": "🧊 Забастовка: Киборги-шахтеры объявили бойкот. Рынок Золота упал на -10%.", "m": 0,
                 "tgt": "Золото", "mult": 0.90},
                {"t": "📡 Подписка: Забыл отключить тестовый период продвинутой аналитики: -1,000$.", "m": -1000,
                 "tgt": None},
                {"t": "🎭 Фейк-ньюс: В сети пустили слух о твоем крахе. Потрачено на очистку репутации: -4,000$.",
                 "m": -4000, "tgt": None},
                {"t": "📉 Коррекция рынка: Общая усталость инвесторов. Все активы просели на -10%.", "m": 0,
                 "tgt": "all_down", "mult": 0.90}
            ]
            evt = random.choice(bad_events)
            state["money"] += evt["m"]
            if evt["tgt"] == "all_down":
                for k in state["prices"]: state["prices"][k] = int(state["prices"][k] * evt["mult"])
            elif evt["tgt"] and evt["tgt"] in state["prices"]:
                state["prices"][evt["tgt"]] = int(state["prices"][evt["tgt"]] * evt["mult"])
            log_message(evt["t"], "#FF4A4A")

    def buy_asset(asset_name):
        if state["mafia_active"]: return
        price = state["prices"][asset_name]
        if state["money"] >= price:
            state["money"] -= price
            state["assets"][asset_name] = state["assets"].get(asset_name, 0) + 1
            log_message(f"Куплено: {asset_name}", "#4AFF4A")
            update_ui()

    def sell_asset(asset_name):
        if state["mafia_active"]: return
        if state["assets"].get(asset_name, 0) > 0:
            state["money"] += state["prices"][asset_name]
            state["assets"][asset_name] -= 1
            log_message(f"Продано: {asset_name}", "#FFB04A")
            update_ui()

    capital_text = ft.Text(value="0$", size=34, weight="bold", color="#4AFF4A")
    balance_text = ft.Text(value="0$", size=14, color="#B0B5C0")
    loan_text = ft.Text(value="Долг: 0$", size=14, color="#FF4A4A", weight="bold")
    turn_text = ft.Text(value="ДЕНЬ: 1", size=14, weight="bold")
    level_status_text = ft.Text(value="УРОВЕНЬ 1", size=14, weight="bold", color="#4ABFFF")
    log_column = ft.Column(scroll=ft.ScrollMode.ALWAYS, height=110)
    market_rows = ft.Column()

    bots_status_text = ft.Text("Боты: 0", size=12, color="#707580")
    lawyer_status_text = ft.Text("Адвокат: Нет", size=12, color="#707580")
    mafia_title_text = ft.Text("! ТРЕБОВАНИЕ ВЫКУПА", color="#FF4A4A", weight="bold", size=14)
    mafia_desc_text = ft.Text("", color="#FFFFFF", size=12, text_align=ft.TextAlign.CENTER)
    mafia_pay_btn = ft.Container()

    mafia_banner = ft.Container(
        visible=False, padding=12, bgcolor="#3a1c1c", border_radius=10,
        content=ft.Column([
            ft.Row([mafia_title_text], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([mafia_desc_text], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=4),
            ft.Row([
                mafia_pay_btn,
                make_btn("Игнорировать", refuse_ransom_click, bg="#707580", color="#FFFFFF")
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

    level_banner = ft.Container(
        visible=False, padding=12, bgcolor="#1c3a27", border_radius=10,
        content=ft.Column([
            ft.Row([ft.Text("🚀 ЦЕЛЬ ДОСТИГНУТА!", color="#4AFF4A", weight="bold", size=15)],
                   alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([make_btn("Запустить следующий этап", level_up_click, bg="#4AFF4A", color="#121418")],
                   alignment=ft.MainAxisAlignment.CENTER)
        ])
    )

    game_over_banner = ft.Container(
        visible=False, padding=15, bgcolor="#1A1D24", border_radius=10,
        content=ft.Row([ft.Text(value="", size=16, weight="bold", text_align=ft.TextAlign.CENTER)],
                       alignment=ft.MainAxisAlignment.CENTER)
    )

    def log_message(text, color="#B0B5C0"):
        log_column.controls.insert(0, ft.Text(text, color=color, size=12))
        if len(log_column.controls) > 8: log_column.controls.pop()

    def update_ui():
        total_capital = get_total_capital()
        capital_text.value = f"{total_capital:,}$"
        balance_text.value = f"Наличные: {state['money']:,}$"
        loan_text.value = f"Долг банку: {state['loan']:,}$" if state["loan"] > 0 else "Долгов нет"
        loan_text.color = "#FF4A4A" if state["loan"] > 0 else "#707580"
        turn_text.value = f"ДЕНЬ: {state['turn']}"
        level_status_text.value = f"УРОВЕНЬ {state['level']} (Цель: {state['goal']:,}$)"
        bots_status_text.value = f"Боты: {state['bots_count']} (+{state['bots_count'] * 1500:,}$/х)"
        lawyer_status_text.value = "Адвокат: Активен" if state["has_lawyer"] else "Адвокат: Нет"
        bots_status_text.color = "#4AFF4A" if state["bots_count"] > 0 else "#707580"
        lawyer_status_text.color = "#4AFF4A" if state["has_lawyer"] else "#707580"

        if state["mafia_active"]:
            mafia_desc_text.value = f"{state['mafia_text']}"
            mafia_title_text.value = f"СИНДИКАТ: {state['mafia_demand']:,}$"
            mafia_banner.content.controls[3].controls[0] = make_btn(
                f"Заплатить {state['mafia_demand']:,}$",
                pay_ransom_click, bg="#FF4A4A", color="#FFFFFF"
            )

        mafia_banner.visible = state["mafia_active"]
        next_turn_container.disabled = state["mafia_active"]

        if total_capital >= state["goal"] and state["level"] < 3:
            level_banner.visible = True

        if total_capital >= 5000000 and state["level"] == 3:
            game_over_banner.visible = True
            game_over_banner.content.controls[
                0].value = "👑 ФИНАЛ: КВАНТОВЫЙ ВЛАДЫКА!\nВы полностью подмяли под себя экономику."
            game_over_banner.content.controls[0].color = "#4AFF4A"
            next_turn_container.disabled = True
        elif total_capital < -50000 or (state["money"] < 0 and sum(state["assets"].values()) == 0):
            game_over_banner.visible = True
            game_over_banner.content.controls[0].value = "💥 БАНКРОТСТВО!\nДолги или санкции уничтожили ваш фонд."
            game_over_banner.content.controls[0].color = "#FF4A4A"
            next_turn_container.disabled = True

        market_rows.controls.clear()
        for asset, price in state["prices"].items():
            qty = state["assets"].get(asset, 0)
            letter = shortcuts.get(asset, asset)
            asset_trends = state["trends"].get(asset, ["▬", "▬", "▬"])

            trend_row_controls = []
            for char in asset_trends:
                if char == "▲":
                    col = "#4AFF4A"
                elif char == "▼":
                    col = "#FF4A4A"
                else:
                    col = "#707580"
                trend_row_controls.append(ft.Text(char, color=col, size=13, weight="bold"))

            market_rows.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(f"[{letter}] {asset}", weight="bold", width=115, size=13),
                        ft.Text(f"{price}$", color="#4ABFFF", width=55, size=13),
                        ft.Container(
                            content=ft.Row(trend_row_controls, spacing=1, alignment=ft.MainAxisAlignment.START),
                            width=35),
                        ft.Text(f"{qty} ед.", color="#B0B5C0", width=50, size=13),
                        ft.Row([
                            make_btn("+", lambda e, a=asset: buy_asset(a), width=35, height=30),
                            make_btn("-", lambda e, a=asset: sell_asset(a), width=35, height=30),
                        ], spacing=5)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=6, bgcolor="#1A1D24", border_radius=6
                )
            )

        save_game()
        page.update()

    header = ft.Container(
        content=ft.Column([
            ft.Row([level_status_text, turn_text], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([ft.Text("ОБЩИЙ ЧИСТЫЙ КАПИТАЛ", size=11, color="#707580")], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([capital_text], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([balance_text, ft.Text("|", color="#707580"), loan_text], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([bots_status_text, ft.Text("|", color="#707580"), lawyer_status_text],
                   alignment=ft.MainAxisAlignment.CENTER)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=12, bgcolor="#1A1D24", border_radius=10
    )

    log_container = ft.Container(
        content=log_column, padding=10, bgcolor="#1A1D24", border_radius=8, width=330
    )

    next_turn_container = make_btn("ЗАВЕРШИТЬ ТЕКУЩИЙ ДЕНЬ", next_turn_click, bg="#4AFF4A", color="#121418", width=240,
                                   height=45)

    page.add(
        header,
        mafia_banner,
        level_banner,
        game_over_banner,
        ft.Row([ft.Text("БАНКОВСКОЕ КРЕДИТОВАНИЕ (5%)", size=12, weight="bold", color="#707580")],
               alignment=ft.MainAxisAlignment.CENTER),
        ft.Container(content=ft.Row([make_btn("Взять 10к", borrow_click), make_btn("Вернуть 10к", repay_click)],
                                    alignment=ft.MainAxisAlignment.CENTER, spacing=15)),
        ft.Row([ft.Text("КИБЕР-ИНФРАСТРУКТУРА", size=12, weight="bold", color="#707580")],
               alignment=ft.MainAxisAlignment.CENTER),
        ft.Container(
            content=ft.Row([make_btn("🤖 Бот (25к)", buy_bot_click), make_btn("🛡 Адвокат (50к)", buy_lawyer_click)],
                           alignment=ft.MainAxisAlignment.CENTER, spacing=15)),
        ft.Row([ft.Text("РЫНОК АКТИВОВ", size=12, weight="bold", color="#707580")],
               alignment=ft.MainAxisAlignment.CENTER),
        market_rows,
        ft.Row([ft.Text("ЛЕНТА СОБЫТИЙ СИСТЕМЫ", size=12, weight="bold", color="#707580")],
               alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([log_container], alignment=ft.MainAxisAlignment.CENTER),
        ft.Container(height=5),
        ft.Row([
            next_turn_container,
            make_btn("🔄 Сброс", reset_game_click, bg="#252830", color="#FF4A4A")
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)
    )

    if is_loaded:
        log_message(f"💾 Игра успешно возобновлена с дня {state['turn']}!", "#4AFF4A")
    update_ui()


if __name__ == "__main__":
    ft.app(target=main)