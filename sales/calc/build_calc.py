"""Сборка Excel-калькулятора ангара «Поколения».

Правила расчёта металла, оболочки и гражданской части восстановлены по наблюдениям
за публичным конструктором П³ (76 прогонов, ноябрь 2026, см. лист «Сверка с П³» и
sales/p3-vs-kp-18x30.md). Режим «КП (фермы)», сваи, пол из ПАГ и цены — из КП
«Ангар 18×30×6» и КП №192 «Поколения».
"""
import json, math, os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.comments import Comment
from openpyxl.utils import get_column_letter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'Калькулятор_ангара_Поколения.xlsx')

F = 'Arial'
f_norm = Font(name=F, size=10)
f_bold = Font(name=F, size=10, bold=True)
f_h1 = Font(name=F, size=14, bold=True, color='FFFFFF')
f_h2 = Font(name=F, size=11, bold=True, color='1F2A44')
f_in = Font(name=F, size=10, color='0000FF')
f_link = Font(name=F, size=10, color='008000')
f_note = Font(name=F, size=9, italic=True, color='666666')
fill_h1 = PatternFill('solid', fgColor='1F2A44')
fill_in = PatternFill('solid', fgColor='FFF2CC')
fill_sec = PatternFill('solid', fgColor='E8ECF4')
fill_tot = PatternFill('solid', fgColor='FDE9D9')
thin = Side(style='thin', color='BFBFBF')
box = Border(left=thin, right=thin, top=thin, bottom=thin)
NUM = '#,##0;-#,##0;"-"'
NUM1 = '#,##0.0;-#,##0.0;"-"'
NUM2 = '#,##0.00;-#,##0.00;"-"'
RUB = '#,##0" ₽";-#,##0" ₽";"-"'

wb = Workbook()
names = {}


def name(nm, sheet, cell):
    ref = f"'{sheet}'!${''.join(c for c in cell if c.isalpha())}${''.join(c for c in cell if c.isdigit())}"
    wb.defined_names[nm] = DefinedName(nm, attr_text=ref)
    names[nm] = ref


def title(ws, text, sub=None, width=6):
    ws['A1'] = text
    ws['A1'].font = f_h1
    for c in range(1, width + 1):
        ws.cell(row=1, column=c).fill = fill_h1
    ws.row_dimensions[1].height = 24
    if sub:
        ws['A2'] = sub
        ws['A2'].font = f_note


def section(ws, r, text, width=6):
    ws.cell(row=r, column=1, value=text).font = f_h2
    for c in range(1, width + 1):
        ws.cell(row=r, column=c).fill = fill_sec


# ---------------------------------------------------------------- Ввод
wi = wb.active
wi.title = 'Ввод'
title(wi, 'Калькулятор ангара «Поколения» — исходные данные', 'Жёлтые ячейки с синим текстом — вводите свои значения. Остальные листы считаются сами.', 4)
wi.column_dimensions['A'].width = 46
wi.column_dimensions['B'].width = 22
wi.column_dimensions['C'].width = 10
wi.column_dimensions['D'].width = 70

inputs = [
    ('Геометрия', None),
    ('L', 'Длина здания, м', 30, 'м', 'Вдоль конька'),
    ('B', 'Ширина (пролёт), м', 18, 'м', 'Один пролёт'),
    ('H', 'Высота до карниза, м', 6, 'м', ''),
    ('STEP', 'Шаг рам, м', 6, 'м', 'Типично 6 м'),
    ('SLOPE', 'Уклон кровли, градусы', 5.71, '°', '10 % = 5,71°; 8° по умолчанию в П³'),
    ('Нагрузки и грунт', None),
    ('SNOW', 'Снеговая нагрузка, кПа', 1.8, 'кПа', 'См. справочник: снеговые районы по СП 20.13330'),
    ('FLOORLOAD', 'Нагрузка на пол, т/м²', 1, 'т/м²', 'Для монолитной плиты (как в П³)'),
    ('SOIL', 'Грунт', 'Обычный', '', 'Обычный / Торф (слабый) — торф увеличивает фундаменты и плиту'),
    ('Конструкция', None),
    ('SCHEME', 'Схема каркаса', 'КП (фермы)', '', 'П³ (балки) — как конструктор П³; КП (фермы) — как КП 18×30'),
    ('FACHWERK', 'Фахверковые колонны на торцах', 'да', '', 'да / нет'),
    ('WALLLAYOUT', 'Раскладка стеновых панелей', 'вертикальная', '', 'горизонтальная (П³, без ригелей) / вертикальная (ригели стен, как КП)'),
    ('BASE', 'Основание стен', 'швеллер', '', 'цоколь (монолит 0,6 м, как П³) / швеллер (нижний прогон, как КП)'),
    ('NODEPCT', 'Узлы, пластины, болты, % от массы', 0.093, '%', 'КП 18×30: 2,4 т на 25,8 т = 9,3 %'),
    ('Оболочка', None),
    ('PANELTYPE', 'Утеплитель панелей', 'минвата', '', 'минвата / PIR'),
    ('WALLTHK', 'Толщина стеновых панелей, мм', 100, 'мм', '60–250'),
    ('ROOFTHK', 'Толщина кровельных панелей, мм', 120, 'мм', '80–250'),
    ('OVH_END', 'Свес кровли по торцам (с каждой стороны), м', '', 'м', 'Пусто = авто: П³ 1,0 м; КП 0,5 м'),
    ('OVH_EAVE', 'Свес кровли по карнизу, м (по скату)', '', 'м', 'Пусто = авто: П³ 0,58 м; КП 0'),
    ('Фундамент и пол', None),
    ('FOUND', 'Фундамент', 'винтовые сваи', '', 'монолит (столбчатые, как П³) / винтовые сваи (как КП)'),
    ('PILESPERCOL', 'Свай под одну колонну, шт', 2, 'шт', 'КП: 2 сваи Ø133 с оголовком'),
    ('FLOOR', 'Пол', 'плиты ПАГ', '', 'монолитная плита (как П³) / плиты ПАГ (как КП) / нет'),
    ('Проёмы и опции', None),
    ('GATES', 'Ворота, шт', 0, 'шт', 'КП 18×30: не входят'),
    ('WINDOWS', 'Окна, м²', 0, 'м²', ''),
    ('DOORS', 'Двери, шт', 0, 'шт', 'Цена в справочнике пустая — заполните'),
    ('FLASH', 'Доборы и крепёж панелей включить в смету', 'нет', '', 'да / нет (КП 18×30: не входят)'),
    ('GUTTER', 'Водосток и снегозадержание', 'нет', '', 'да / нет'),
    ('DELIVERY', 'Доставка металла и панелей', 'нет', '', 'да / нет (КП 18×30: не входит)'),
    ('Коммерция', None),
    ('DESIGN', 'Проектирование (КЖ, КМ, геология), ₽', 420000, '₽', 'КП 18×30'),
    ('MARKUP', 'Наценка к итогу, %', 0, '%', 'Применяется ко всей смете'),
    ('VAT', 'Ставка НДС (цены в справочнике с НДС)', 0.05, '%', 'КП 18×30: НДС 5 %'),
]
r = 4
dv_lists = {
    'SOIL': '"Обычный,Торф"', 'SCHEME': '"П³ (балки),КП (фермы)"', 'FACHWERK': '"да,нет"',
    'WALLLAYOUT': '"горизонтальная,вертикальная"', 'BASE': '"цоколь,швеллер"', 'PANELTYPE': '"минвата,PIR"',
    'FOUND': '"монолит,винтовые сваи"', 'FLOOR': '"монолитная плита,плиты ПАГ,нет"', 'FLASH': '"да,нет"',
    'GUTTER': '"да,нет"', 'DELIVERY': '"да,нет"', 'WALLTHK': '"60,80,100,120,150,200,250"',
    'ROOFTHK': '"80,100,120,150,180,200,250"',
}
for it in inputs:
    if it[1] is None:
        section(wi, r, it[0], 4)
        r += 1
        continue
    key, label, val, unit, note = it
    wi.cell(row=r, column=1, value=label).font = f_norm
    c = wi.cell(row=r, column=2, value=val)
    c.font = f_in
    c.fill = fill_in
    c.border = box
    if key in ('NODEPCT', 'MARKUP', 'VAT'):
        c.number_format = '0.0%'
    elif isinstance(val, (int, float)) and key not in ('WALLTHK', 'ROOFTHK'):
        c.number_format = '#,##0.##'
    wi.cell(row=r, column=3, value=unit).font = f_note
    wi.cell(row=r, column=4, value=note).font = f_note
    name(key, 'Ввод', f'B{r}')
    if key in dv_lists:
        dv = DataValidation(type='list', formula1=dv_lists[key], allow_blank=True)
        wi.add_data_validation(dv)
        dv.add(f'B{r}')
    r += 1
r += 1
wi.cell(row=r, column=1, value='Пример заполнен по КП «Ангар 18 × 30 м, высота 6 м» (ноябрь 2026) — итог должен совпасть с КП: 15 900 203 ₽.').font = f_note
r += 1
wi.cell(row=r, column=1, value='Итог сметы, ₽ (с НДС)').font = f_bold
wi.cell(row=r, column=2, value='=TOTAL_SUM').number_format = RUB
wi.cell(row=r, column=2).font = Font(name=F, size=12, bold=True, color='008000')
r += 1
wi.cell(row=r, column=1, value='Цена за м² застройки, ₽').font = f_bold
wi.cell(row=r, column=2, value='=TOTAL_SUM/(L*B)').number_format = RUB
wi.cell(row=r, column=2).font = Font(name=F, size=11, bold=True, color='008000')
r += 1
wi.cell(row=r, column=1, value='Металлоконструкции, т').font = f_bold
wi.cell(row=r, column=2, value='=STEEL_T').number_format = NUM1
wi.cell(row=r, column=2).font = f_link
wi.freeze_panes = 'A4'

# ---------------------------------------------------------------- Справочник
ws = wb.create_sheet('Справочник')
title(ws, 'Справочник: профили, таблицы подбора, цены', 'Цены — с НДС 5 %. Источник указан в столбце «Источник». Пустая цена = позиция не войдёт в смету, пока не заполните.', 5)
for col, w in zip('ABCDE', (44, 16, 12, 16, 60)):
    ws.column_dimensions[col].width = w
r = 4
section(ws, r, 'Масса профилей, кг/м', 5); r += 1
for h, c in zip(('Профиль', 'кг/м', '', '', 'Источник'), 'ABCDE'):
    ws[f'{c}{r}'] = h; ws[f'{c}{r}'].font = f_bold
r += 1
prof_start = r
profiles = [
    ('40К1', 72.6, 'П³: колонна (масса/длина из спецификации). Внимание: по сортаменту 40К1 ≈ 138 кг/м'),
    ('55Б1', 82.52, 'П³: стропильная балка'), ('45Б1', 59.83, 'П³: стропильная балка (малые пролёты)'),
    ('30Б1', 32.9, 'П³: карнизная балка'), ('35Б1', 38.9, 'П³: карнизная балка, шаг 7,5 м'),
    ('40Б1', 48.1, 'Сортамент (П³ для шага 7,5 м и длины > 36 м)'), ('20Б1', 21.3, 'П³: связи'),
    ('Z300', 11.5, 'П³: прогон Зет-профиль 300'), ('Z250', 8.8, 'П³: прогон Зет-профиль 250'),
    ('Колонна КП (К1)', 98.3, 'КП 18×30: 7 080 кг / 12 шт / 6 м'),
    ('Ферма КП, на 1 м пролёта', 62.2, 'КП 18×30: 6 720 кг / 6 шт / 18 м'),
    ('Прогон КП (П1)', 18.33, 'КП 18×30: 4 400 кг / 40 шт / 6 м'),
    ('Ригель стены КП (Ж1)', 14.67, 'КП 18×30: 4 224 кг / 288 м'),
    ('Фахверк КП (К2)', 40.0, 'КП 18×30: 1 040 кг / 4 шт / ~6,5 м'),
    ('Швеллер нижнего прогона', 12.5, 'КП 18×30: 1 200 кг / 96 м'),
]
for p, kg, src in profiles:
    ws[f'A{r}'] = p; ws[f'B{r}'] = kg; ws[f'B{r}'].font = f_in; ws[f'B{r}'].fill = fill_in; ws[f'B{r}'].number_format = '0.00'
    ws[f'E{r}'] = src; ws[f'E{r}'].font = f_note
    r += 1
prof_end = r - 1
wb.defined_names['PROF_NAMES'] = DefinedName('PROF_NAMES', attr_text=f"'Справочник'!$A${prof_start}:$A${prof_end}")
wb.defined_names['PROF_KG'] = DefinedName('PROF_KG', attr_text=f"'Справочник'!$B${prof_start}:$B${prof_end}")
r += 1

section(ws, r, 'Шаг прогонов (как в П³), м', 5); r += 1
ws[f'A{r}'] = 'Снег до, кПа'; ws[f'B{r}'] = 'Шаг, м'; ws[f'A{r}'].font = f_bold; ws[f'B{r}'].font = f_bold; r += 1
ps_start = r
for snow, s in ((0, 2.4), (1.25, 2.0), (2.2, 1.6), (3.6, 1.33)):
    ws[f'A{r}'] = snow; ws[f'B{r}'] = s
    ws[f'B{r}'].font = f_in; ws[f'B{r}'].fill = fill_in
    ws[f'E{r}'] = 'Нижняя граница диапазона снега; подобрано по 76 моделям П³'; ws[f'E{r}'].font = f_note
    r += 1
wb.defined_names['PS_SNOW'] = DefinedName('PS_SNOW', attr_text=f"'Справочник'!$A${ps_start}:$A${r-1}")
wb.defined_names['PS_STEP'] = DefinedName('PS_STEP', attr_text=f"'Справочник'!$B${ps_start}:$B${r-1}")
ws[f'A{r}'] = 'Коэф. к шагу при кровле ≤ 80 мм / ≥ 150 мм'; ws[f'B{r}'] = 0.8; ws[f'C{r}'] = 1.2
for c in 'BC':
    ws[f'{c}{r}'].font = f_in; ws[f'{c}{r}'].fill = fill_in
name('PS_K80', 'Справочник', f'B{r}'); name('PS_K150', 'Справочник', f'C{r}')
r += 2

section(ws, r, 'Монолитная плита пола (как в П³)', 5); r += 1
for h, c in zip(('Нагрузка до, т/м²', 'Толщина, мм', 'Арматура, кг/м²', 'Песок / щебень, м', 'Источник'), 'ABCDE'):
    ws[f'{c}{r}'] = h; ws[f'{c}{r}'].font = f_bold
r += 1
sl_start = r
for load, t, kg, sand, grav, txt in ((0, 150, 8.64, 0.10, 0.15, 'Ø10/150, 1 сетка'), (0.75, 180, 18.67, 0.12, 0.18, 'Ø12/200, 2 сетки'),
                                    (2.5, 220, 24.89, 0.15, 0.20, 'Ø12/150, 2 сетки'), (4, 260, 33.88, 0.18, 0.25, 'Ø14/150, 2 сетки')):
    ws[f'A{r}'] = load; ws[f'B{r}'] = t; ws[f'C{r}'] = kg; ws[f'D{r}'] = sand; ws[f'F{r}'] = grav
    ws[f'E{r}'] = f'П³: {txt}; щебень в столбце F'; ws[f'E{r}'].font = f_note
    for c in 'BCDF':
        ws[f'{c}{r}'].font = f_in; ws[f'{c}{r}'].fill = fill_in
    r += 1
for nm, col in (('SL_LOAD', 'A'), ('SL_T', 'B'), ('SL_KG', 'C'), ('SL_SAND', 'D'), ('SL_GRAV', 'F')):
    wb.defined_names[nm] = DefinedName(nm, attr_text=f"'Справочник'!${col}${sl_start}:${col}${r-1}")
r += 1

section(ws, r, 'Снеговые районы (СП 20.13330, вес снегового покрова)', 5); r += 1
for reg, kpa in (('I', 0.5), ('II', 1.0), ('III', 1.5), ('IV', 2.0), ('V', 2.5), ('VI', 3.0), ('VII', 3.5), ('VIII', 4.0)):
    ws[f'A{r}'] = f'Район {reg}'; ws[f'B{r}'] = kpa; ws[f'E{r}'] = 'Справочно: Москва — III, Санкт-Петербург — III'
    ws[f'E{r}'].font = f_note
    r += 1
r += 1

section(ws, r, 'Цены (с НДС 5 %)', 5); r += 1
for h, c in zip(('Позиция', 'Цена', 'Ед.', '', 'Источник'), 'ABCDE'):
    ws[f'{c}{r}'] = h; ws[f'{c}{r}'].font = f_bold
r += 1
prices = [
    ('P_STEEL_MFG', 'Изготовление металлоконструкций', 152250, 'т', 'КП 18×30'),
    ('P_STEEL_MNT', 'Монтаж металлоконструкций', 36750, 'т', 'КП 18×30'),
    ('P_PAINT', 'Окраска МК (грунт-эмаль + работы)', 16755.32, 'т', 'КП 18×30: 472 500 ₽ / 28,2 т'),
    ('P_CRANE', 'Автокран на монтаже МК', 33800, 'смена', 'КП 18×30; смен = ОКРВВЕРХ(т / 6)'),
    ('P_WALL', 'Стеновые панели', '=IF(WALLTHK=100,2971.5,IF(WALLTHK=120,3349.5,""))', 'м²', 'КП 18×30 (100 мм); КП №192 (120 мм, 3 190 без НДС × 1,05). Другие толщины — впишите'),
    ('P_ROOF', 'Кровельные панели', '=IF(ROOFTHK=120,3255,IF(ROOFTHK=150,3927,""))', 'м²', 'КП 18×30 (120 мм); КП №192 (150 мм, 3 740 × 1,05)'),
    ('P_PANEL_MNT', 'Монтаж сэндвич-панелей', 1260, 'м²', 'КП 18×30'),
    ('P_FLASH', 'Доборы, фасонка, крепёж', 482.6, 'м² оболочки', 'КП №192: 1 350 000 ₽ / 2 937 м² × 1,05'),
    ('P_GUTTER', 'Водосток', 2520, 'м', 'КП №192: 2 400 × 1,05'),
    ('P_SNOWGUARD', 'Снегозадержатели', 2520, 'м', 'КП №192: 2 400 × 1,05'),
    ('P_PILE', 'Винтовая свая Ø133 с оголовком, вкручивание', 30187.5, 'шт', 'КП 18×30'),
    ('P_FOOTING', 'Столбчатый монолитный фундамент (ростверк)', 68040, 'шт', 'КП №192: 64 800 × 1,05'),
    ('P_EARTH', 'Разработка грунта с вывозом (под фундаменты)', 1890, 'м³', 'КП №192: 1 800 × 1,05; объём = бетон × 2'),
    ('P_PLINTH', 'Монолитный цоколь', '', 'м³', 'Нет данных — впишите'),
    ('P_PAG', 'Пол из плит ПАГ по щебню, под ключ', 6499, 'м²', 'КП 18×30 (плиты, щебень, геотекстиль, техника, кран, швы)'),
    ('P_SLAB', 'Монолитная плита пола с подушкой', 47250, 'м³ бетона', 'КП №192: 45 000 × 1,05 (h = 200 мм, двойное армирование)'),
    ('P_GATE', 'Ворота секционные 3×3,5 м с автоматикой', 493500, 'шт', 'КП №192: 470 000 × 1,05'),
    ('P_WINDOW', 'Окна ПВХ', 17115, 'м²', 'КП №192: 16 300 × 1,05'),
    ('P_DOOR', 'Дверь', '', 'шт', 'Нет данных — впишите'),
    ('P_DELIV_STEEL', 'Доставка МК, за рейс', 44100, 'рейс', 'КП №192: 42 000 × 1,05; ~8,5 т на рейс'),
    ('P_DELIV_PANEL', 'Доставка панелей, за рейс', 50400, 'рейс', 'КП №192: 48 000 × 1,05; ~490 м² на рейс'),
]
for key, label, val, unit, src in prices:
    ws[f'A{r}'] = label; ws[f'B{r}'] = val; ws[f'C{r}'] = unit; ws[f'E{r}'] = src
    ws[f'B{r}'].font = f_in; ws[f'B{r}'].fill = fill_in; ws[f'B{r}'].number_format = '#,##0.00'
    ws[f'E{r}'].font = f_note
    name(key, 'Справочник', f'B{r}')
    r += 1

# ---------------------------------------------------------------- Расчёт
wc = wb.create_sheet('Расчёт')
title(wc, 'Расчёт объёмов', 'Все величины — формулы от листа «Ввод». Столбец D: откуда правило.', 4)
for col, w in zip('ABCD', (52, 16, 10, 78)):
    wc.column_dimensions[col].width = w
r = 4


def row(key, label, formula, unit, note, fmt=NUM2):
    global r
    wc.cell(row=r, column=1, value=label).font = f_norm
    c = wc.cell(row=r, column=2, value=formula)
    c.font = f_norm
    c.number_format = fmt
    wc.cell(row=r, column=3, value=unit).font = f_note
    wc.cell(row=r, column=4, value=note).font = f_note
    if key:
        name(key, 'Расчёт', f'B{r}')
    r += 1


def sec(text):
    global r
    r += 1
    section(wc, r, text, 4)
    r += 1


sec('Геометрия')
row('IS_P3', 'Режим П³ (1) / КП (0)', '=IF(SCHEME="П³ (балки)",1,0)', '', '', NUM)
row('NB', 'Число шагов рам', '=MAX(1,ROUND(L/STEP,0))', 'шт', 'П³: рам = шагов + 1', NUM)
row('FRAMES', 'Число рам', '=NB+1', 'шт', '', NUM)
row('ALPHA', 'Уклон, рад', '=RADIANS(SLOPE)', '', '')
row('LS', 'Длина ската, м', '=B/2/COS(ALPHA)', 'м', '')
row('PER', 'Периметр, м', '=2*(L+B)', 'м', '')
row('AREA', 'Площадь застройки, м²', '=L*B', 'м²', '')
row('PLINTH_H', 'Высота цоколя, м', '=IF(BASE="цоколь",0.6,0)', 'м', 'П³: монолитный цоколь 0,6 м; панели начинаются над ним')
row('OVH_E', 'Свес по торцам, м', '=IF(OVH_END="",IF(IS_P3=1,1,0.5),OVH_END)', 'м', 'П³: кровля длиннее здания на 2 м; КП: на 1 м')
row('OVH_V', 'Свес по карнизу (по скату), м', '=IF(OVH_EAVE="",IF(IS_P3=1,0.58,0),OVH_EAVE)', 'м', 'П³: +0,58 м к скату')
row('FACH_N', 'Колонн фахверка (оба торца)', '=IF(FACHWERK="да",2*MAX(0,ROUND(B/6,0)-1),0)', 'шт', 'КП 18×30: 4 шт при пролёте 18 м', NUM)

sec('Металлоконструкции')
row('COLS', 'Колонны рам, шт', '=2*FRAMES', 'шт', 'П³ и КП', NUM)
row('COL_KG', 'Колонны рам, кг', '=IF(IS_P3=1,COLS*(H+0.3)*INDEX(PROF_KG,MATCH("40К1",PROF_NAMES,0)),COLS*H*INDEX(PROF_KG,MATCH("Колонна КП (К1)",PROF_NAMES,0)))', 'кг', 'П³: 40К1, длина H+0,3 м. КП: 98,3 кг/м', NUM)
row('RAF_PROF', 'Профиль стропильной балки (П³)', '=IF(AND(B<=12,SNOW<=1),"45Б1","55Б1")', '', 'П³: 45Б1 только при пролёте ≤ 12 м и снеге ≤ 1 кПа', '@')
row('RAF_KG', 'Стропильные балки / фермы, кг', '=IF(IS_P3=1,2*FRAMES*(LS-0.24)*INDEX(PROF_KG,MATCH(RAF_PROF,PROF_NAMES,0)),FRAMES*B*INDEX(PROF_KG,MATCH("Ферма КП, на 1 м пролёта",PROF_NAMES,0)))', 'кг', 'П³: 2 балки на раму длиной (скат − 0,24 м). КП: ферма 62,2 кг на 1 м пролёта', NUM)
row('EDGE_PROF', 'Профиль карнизной балки (П³)', '=IF(STEP<=6,"30Б1",IF(L<=36,"35Б1","40Б1"))', '', 'П³', '@')
row('EDGE_KG', 'Карнизные балки, кг', '=IF(IS_P3=1,2*L*INDEX(PROF_KG,MATCH(EDGE_PROF,PROF_NAMES,0)),0)', 'кг', 'П³: 2 линии на всю длину. В КП карнизный прогон входит в прогоны', NUM)
row('PURL_PROF', 'Профиль прогона (П³)', '=IF(STEP<=5,"Z250","Z300")', '', 'П³', '@')
row('PURL_STEP', 'Шаг прогонов, м', '=INDEX(PS_STEP,MATCH(SNOW,PS_SNOW,1))*IF(ROOFTHK<=80,PS_K80,IF(ROOFTHK>=150,PS_K150,1))', 'м', 'Подобрано по П³: зависит от снега и толщины кровли')
row('PURL_ROWS', 'Рядов прогонов', '=IF(IS_P3=1,ROUND(2*LS/PURL_STEP,0)+1,2*ROUNDUP(LS/2.5,0))', 'шт', 'П³: ОКРУГЛ(2·скат/шаг)+1. КП: 4 ряда на скат при скате 9 м', NUM)
row('PURL_PCS', 'Прогонов, шт', '=PURL_ROWS*NB', 'шт', '', NUM)
row('PURL_KG', 'Прогоны, кг', '=PURL_ROWS*L*IF(IS_P3=1,INDEX(PROF_KG,MATCH(PURL_PROF,PROF_NAMES,0)),INDEX(PROF_KG,MATCH("Прогон КП (П1)",PROF_NAMES,0)))', 'кг', '', NUM)
row('BRW_PCS', 'Связи по стенам, шт', '=IF(IS_P3=1,4*MAX(2,ROUNDUP(NB/3,0)),4*MAX(1,ROUNDUP(NB/5,0)))', 'шт', 'П³: 4 на связевую панель, панелей = max(2; шагов/3). КП: 4 шт на 30 м', NUM)
row('BRW_KG', 'Связи по стенам, кг', '=IF(IS_P3=1,BRW_PCS*SQRT(STEP^2+(H-0.7)^2)*INDEX(PROF_KG,MATCH("20Б1",PROF_NAMES,0)),BRW_PCS*180)', 'кг', 'П³: 20Б1 по диагонали панели. КП: СВ1 180 кг/шт', NUM)
row('BRR_PCS', 'Связи по кровле, шт (на один скат)', '=IF(IS_P3=1,2*ROUNDUP(NB/2,0)*IF(B>=21,2,1),0)', 'шт', 'П³: есть всегда; КП: без связей по кровле', NUM)
row('BRR_KG', 'Связи по кровле, кг', '=2*BRR_PCS*SQRT(STEP^2+IF(B<21,LS,LS/2)^2)*INDEX(PROF_KG,MATCH("20Б1",PROF_NAMES,0))', 'кг', 'П³: 20Б1, оба ската', NUM)
row('KNEE_KG', 'Укосины торцевых стен, кг', '=IF(IS_P3=1,0,4*104)', 'кг', 'КП: УК1 4 × 104 кг', NUM)
row('FACH_KG', 'Фахверк, кг', '=FACH_N*(H+B/4*TAN(ALPHA))*INDEX(PROF_KG,MATCH("Фахверк КП (К2)",PROF_NAMES,0))', 'кг', 'КП', NUM)
row('GIRT_ROWS', 'Рядов ригелей стен', '=IF(WALLLAYOUT="вертикальная",ROUNDUP(H/2,0),0)', 'шт', 'КП: 3 ряда при H = 6 м', NUM)
row('GIRT_KG', 'Ригели стен, кг', '=GIRT_ROWS*PER*INDEX(PROF_KG,MATCH("Ригель стены КП (Ж1)",PROF_NAMES,0))', 'кг', 'КП', NUM)
row('CHAN_KG', 'Нижний прогон-швеллер, кг', '=IF(BASE="швеллер",PER*INDEX(PROF_KG,MATCH("Швеллер нижнего прогона",PROF_NAMES,0)),0)', 'кг', 'КП', NUM)
row('STEEL_NET', 'Итого элементы, кг', '=COL_KG+RAF_KG+EDGE_KG+PURL_KG+BRW_KG+BRR_KG+KNEE_KG+FACH_KG+GIRT_KG+CHAN_KG', 'кг', '', NUM)
row('NODE_KG', 'Узлы, пластины, болты, кг', '=STEEL_NET*NODEPCT', 'кг', 'П³ не даёт массу пластин; % из КП', NUM)
row('STEEL_T', 'МЕТАЛЛОКОНСТРУКЦИИ ВСЕГО, т', '=ROUND((STEEL_NET+NODE_KG)/1000,1)', 'т', '', NUM1)
row('STEEL_T_P3', 'Для сверки: масса «как в П³» (без узлов), т', '=ROUND((COL_KG+RAF_KG+EDGE_KG+PURL_KG+BRW_KG+BRR_KG)/1000,1)', 'т', 'Сравнивайте с полем «МК, т» в П³ (режим П³)', NUM1)

sec('Оболочка (сэндвич-панели)')
row('WALL_M2', 'Стеновые панели, м²', '=ROUND(PER*(H-PLINTH_H)+B^2*TAN(ALPHA)/2,0)', 'м²', 'Геометрия: стены + 2 фронтона. В П³ фронтоны учтены дважды (+B²·tg α/2)')
row('ROOF_M2', 'Кровельные панели, м²', '=ROUND(2*(L+2*OVH_E)*(LS+OVH_V),0)', 'м²', 'П³: 2·(L+2)·(скат+0,58); КП: 2·(L+1)·скат')
row('SHELL_M2', 'Оболочка всего, м²', '=WALL_M2+ROOF_M2', 'м²', '')
row('WALL_ROWS', 'Рядов стеновых панелей (горизонтально, ширина 1 м)', '=ROUNDUP(H-PLINTH_H,0)', 'шт', 'П³', NUM)
row('ROOF_PCS', 'Кровельных панелей, шт', '=2*ROUNDUP(L+2*OVH_E,0)', 'шт', 'П³: монтажная ширина 1 м', NUM)
row('FL_BASE', 'Цокольная / стартовая планка, м', '=PER', 'м', 'П³')
row('FL_CORNER', 'Угол наружный, м', '=4*(H-PLINTH_H)', 'м', 'П³')
row('FL_EAVE', 'Карнизные планки (каждая из 6 позиций), м', '=2*L', 'м', 'П³: примыкание, карнизная, лобовая, капельник, нижняя, уплотнитель')
row('FL_RIDGE', 'Конёк наружный / внутренний, м', '=L+1.06', 'м', 'П³')
row('FL_RIDGE2', 'Закрывающая планка, уплотнитель, лента у конька, м', '=2*(L+1.06)', 'м', 'П³')
row('FL_GABLE', 'Торцевая/ветровая и фронтонная планки (каждая), м', '=4*(LS+OVH_V)', 'м', 'П³')
row('SCR_HIDDEN', 'Саморез скрытого крепления Z-Lock, шт', '=2*WALL_ROWS*(2*FRAMES+4)+8', 'шт', 'П³: точно на всех 76 прогонах', NUM)
row('SCR_ROOF', 'Саморез кровельный, шт', '=ROOF_PCS*2*(ROUNDUP(LS/PURL_STEP,0)+1)', 'шт', 'П³: 2 на панель на опору', NUM)
row('RIVETS', 'Саморез/заклёпка для доборов, шт', '=ROUND(2064+53.33*(L-30)+20*(B-18)+13.4*(H-6),0)', 'шт', 'Линейная аппроксимация по П³', NUM)
row('TAPE', 'Уплотнительная лента по опорам, м', '=WALL_M2+0.87*PURL_ROWS*L', 'м', 'Аппроксимация по П³')
row('BUTYL', 'Бутилкаучуковый шнур продольных стыков, м', '=0.97*ROOF_M2', 'м', 'Аппроксимация по П³')
row('SEALANT', 'Герметик, картриджей', '=ROUNDUP(0.1*SHELL_M2,0)', 'шт', 'П³', NUM)
row('FOAM', 'Монтажная пена, баллонов', '=ROUNDUP(SHELL_M2/2000,0)', 'шт', 'П³', NUM)

sec('Фундаменты')
row('COLS_ALL', 'Колонн всего (с фахверком)', '=COLS+FACH_N', 'шт', '', NUM)
row('PILES', 'Винтовых свай, шт', '=IF(FOUND="винтовые сваи",COLS_ALL*PILESPERCOL,0)', 'шт', 'КП: 2 сваи под колонну', NUM)
row('FOOT_V1', 'Объём одного столбчатого фундамента, м³', '=MAX(0.923,0.462+0.00411*SNOW*STEP*B/2+0.000993*B*STEP+0.000839*H*STEP)*IF(SOIL="Торф",4.06,1)', 'м³', 'Регрессия по П³ (ошибка ≈ 0,04 м³); торф ×4,06')
row('FOOT_N', 'Столбчатых фундаментов, шт', '=IF(FOUND="монолит",COLS,0)', 'шт', 'П³: под фахверк фундаменты не ставятся', NUM)
row('FOOT_V', 'Бетон фундаментов, м³', '=FOOT_N*FOOT_V1', 'м³', '')
row('FOOT_REBAR', 'Арматура фундаментов, кг', '=FOOT_V*IF(SOIL="Торф",125,95.3)', 'кг', 'П³: 95 кг/м³ (торф 125)', NUM)
row('ANCHORS', 'Анкерные болты, шт', '=4*FOOT_N', 'шт', 'П³: 4 на колонну', NUM)

sec('Цоколь (если выбран)')
row('PL_CONC', 'Бетон цоколя B25, м³', '=IF(BASE="цоколь",PER*0.6*0.2,0)', 'м³', 'П³: 0,6 × 0,2 м по периметру')
row('PL_REBAR', 'Арматура цоколя, кг', '=PL_CONC*110', 'кг', 'П³: 110 кг/м³', NUM)
row('PL_XPS', 'ПЕНОПЛЭКС цоколя 50 мм, м²', '=IF(BASE="цоколь",PER*0.6,0)', 'м²', 'П³')
row('PL_WP', 'Гидроизоляция цоколя, м²', '=IF(BASE="цоколь",PER*0.8,0)', 'м²', 'П³')
row('PL_FORM', 'Опалубка цоколя, м²', '=IF(BASE="цоколь",2*PER*0.6,0)', 'м²', 'П³')

sec('Пол')
row('SLAB_T', 'Толщина монолитной плиты, мм', '=IF(FLOOR="монолитная плита",MAX(INDEX(SL_T,MATCH(FLOORLOAD,SL_LOAD,1)),IF(SOIL="Торф",240,0)),0)', 'мм', 'П³: по нагрузке; торф ≥ 240 мм', NUM)
row('SLAB_V', 'Бетон плиты B25, м³', '=AREA*SLAB_T/1000', 'м³', '')
row('SLAB_REBAR', 'Арматура плиты, кг', '=IF(SLAB_T>0,AREA*INDEX(SL_KG,MATCH(FLOORLOAD,SL_LOAD,1)),0)', 'кг', 'П³', NUM)
row('SLAB_SAND', 'Песок на подушку, м³', '=IF(SLAB_T>0,AREA*MAX(INDEX(SL_SAND,MATCH(FLOORLOAD,SL_LOAD,1)),IF(SOIL="Торф",0.2,0))*1.15,0)', 'м³', 'П³: с запасом 15 %')
row('SLAB_GRAV', 'Щебень на подушку, м³', '=IF(SLAB_T>0,AREA*MAX(INDEX(SL_GRAV,MATCH(FLOORLOAD,SL_LOAD,1)),IF(SOIL="Торф",0.26,0))*1.12,0)', 'м³', 'П³: с запасом 12 %')
row('SLAB_GEO', 'Геотекстиль и ПЭ-мембрана (каждый), м²', '=IF(SLAB_T>0,AREA*1.1,0)', 'м²', 'П³')
row('SLAB_JOINTS', 'Нарезка/герметизация швов, м', '=IF(SLAB_T>0,(ROUNDUP(B/6,0)-1)*L+(ROUNDUP(L/6,0)-1)*B,0)', 'м', 'П³: сетка швов 6 × 6 м')
row('PAG_N', 'Плиты ПАГ 6 × 2 м, шт', '=IF(FLOOR="плиты ПАГ",ROUNDUP(AREA/12,0),0)', 'шт', 'КП 18×30: 45 шт', NUM)
row('PAG_GRAV', 'Щебень фр. 20–40, 250 мм, м³', '=IF(FLOOR="плиты ПАГ",AREA*0.25,0)', 'м³', 'КП 18×30')

sec('Метизы (как в П³)')
row('BOLT_M24', 'Болты M24 8.8, шт', '=12*COLS', 'шт', 'П³: 12 на колонну (узлы рамы)', NUM)
row('BOLT_M20', 'Болты M20 8.8, шт', '=16*NB+8*(BRW_PCS+2*BRR_PCS)', 'шт', 'П³: торцевые пластины балок + фасонки связей', NUM)
row('BOLT_M16', 'Болты M16 8.8, шт', '=4*PURL_PCS', 'шт', 'П³: 4 на прогон', NUM)

sec('Освещение (как в П³)')
row('LED_M', 'Линейные LED-светильники, м', '=ROUND(B/6,0)*0.883*L', 'м', 'П³: ряд на каждые 6 м пролёта')
row('LED_CABLE', 'Лоток и кабель (каждый), м', '=LED_M+B', 'м', 'П³')

sec('Логистика')
row('CRANE_SH', 'Смен автокрана на монтаже МК', '=ROUNDUP(STEEL_T/6,0)', 'смена', 'КП 18×30: 5 смен на 28,2 т', NUM)
row('TRIPS_STEEL', 'Рейсов доставки МК', '=ROUNDUP(STEEL_T/8.5,0)', 'рейс', 'КП №192', NUM)
row('TRIPS_PANEL', 'Рейсов доставки панелей', '=ROUNDUP(SHELL_M2/490,0)', 'рейс', 'КП №192', NUM)

# ---------------------------------------------------------------- Смета
we = wb.create_sheet('Смета')
title(we, 'Стоимость по разделам', 'Цены с НДС. Строки с нулём не входят в выбранную комплектацию.', 6)
for col, w in zip('ABCDEF', (5, 58, 14, 10, 16, 18)):
    we.column_dimensions[col].width = w
hdr = ('№', 'Раздел', 'Объём', 'Ед.', 'Цена с НДС, ₽', 'Сумма с НДС, ₽')
for i, h in enumerate(hdr, 1):
    c = we.cell(row=4, column=i, value=h); c.font = Font(name=F, size=10, bold=True, color='FFFFFF'); c.fill = fill_h1
lines = [
    ('Изготовление металлоконструкций', '=STEEL_T', 'т', '=P_STEEL_MFG'),
    ('Монтаж металлоконструкций', '=STEEL_T', 'т', '=P_STEEL_MNT'),
    ('="Стеновые сэндвич-панели "&PANELTYPE&" "&WALLTHK&" мм"', '=WALL_M2', 'м²', '=P_WALL'),
    ('="Кровельные сэндвич-панели "&PANELTYPE&" "&ROOFTHK&" мм"', '=ROOF_M2', 'м²', '=P_ROOF'),
    ('Монтаж сэндвич-панелей', '=SHELL_M2', 'м²', '=P_PANEL_MNT'),
    ('Доборы, фасонные элементы, крепёж', '=IF(FLASH="да",SHELL_M2,0)', 'м²', '=P_FLASH'),
    ('Винтовые сваи Ø133 с оголовками', '=PILES', 'шт', '=P_PILE'),
    ('Столбчатые монолитные фундаменты', '=FOOT_N', 'шт', '=P_FOOTING'),
    ('Разработка грунта под фундаменты', '=FOOT_V*2', 'м³', '=P_EARTH'),
    ('Монолитный цоколь', '=PL_CONC', 'м³', '=P_PLINTH'),
    ('Пол из плит ПАГ по щебню, с основанием и краном', '=IF(FLOOR="плиты ПАГ",AREA,0)', 'м²', '=P_PAG'),
    ('="Монолитная плита пола "&SLAB_T&" мм с подушкой"', '=SLAB_V', 'м³', '=P_SLAB'),
    ('Проектирование: КЖ, КМ, геология (пакет)', 1, 'пакет', '=DESIGN'),
    ('Окраска металлоконструкций', '=STEEL_T', 'т', '=P_PAINT'),
    ('Автокран на монтаже металлоконструкций', '=CRANE_SH', 'смена', '=P_CRANE'),
    ('Ворота секционные', '=GATES', 'шт', '=P_GATE'),
    ('Окна ПВХ', '=WINDOWS', 'м²', '=P_WINDOW'),
    ('Двери', '=DOORS', 'шт', '=P_DOOR'),
    ('Водосток', '=IF(GUTTER="да",2*L,0)', 'м', '=P_GUTTER'),
    ('Снегозадержатели', '=IF(GUTTER="да",2*L,0)', 'м', '=P_SNOWGUARD'),
    ('Доставка металлоконструкций', '=IF(DELIVERY="да",TRIPS_STEEL,0)', 'рейс', '=P_DELIV_STEEL'),
    ('Доставка сэндвич-панелей', '=IF(DELIVERY="да",TRIPS_PANEL,0)', 'рейс', '=P_DELIV_PANEL'),
]
r = 5
for i, (lab, q, u, p) in enumerate(lines, 1):
    we.cell(row=r, column=1, value=i)
    we.cell(row=r, column=2, value=lab)
    we.cell(row=r, column=3, value=q).number_format = NUM2
    we.cell(row=r, column=4, value=u)
    we.cell(row=r, column=5, value=p).number_format = '#,##0.00;-#,##0.00;"-"'
    we.cell(row=r, column=6, value=f'=IF(OR(E{r}="",C{r}=0),0,ROUND(C{r}*E{r},0))').number_format = NUM
    for cc in range(1, 7):
        we.cell(row=r, column=cc).font = f_norm
        we.cell(row=r, column=cc).border = box
    r += 1
last = r - 1
we.cell(row=r, column=2, value='Сумма по разделам').font = f_bold
we.cell(row=r, column=6, value=f'=SUM(F5:F{last})').number_format = NUM
name('SUBTOTAL', 'Смета', f'F{r}'); r += 1
we.cell(row=r, column=2, value='Наценка').font = f_norm
we.cell(row=r, column=6, value='=ROUND(SUBTOTAL*MARKUP,0)').number_format = NUM
name('MARKUP_SUM', 'Смета', f'F{r}'); r += 1
we.cell(row=r, column=2, value='ИТОГО С НДС').font = Font(name=F, size=11, bold=True)
we.cell(row=r, column=6, value='=SUBTOTAL+MARKUP_SUM').number_format = NUM
we.cell(row=r, column=6).font = Font(name=F, size=11, bold=True)
for cc in range(1, 7):
    we.cell(row=r, column=cc).fill = fill_tot
name('TOTAL_SUM', 'Смета', f'F{r}'); r += 1
we.cell(row=r, column=2, value='в том числе НДС').font = f_norm
we.cell(row=r, column=6, value='=ROUND(TOTAL_SUM*VAT/(1+VAT),0)').number_format = NUM; r += 1
we.cell(row=r, column=2, value='Цена за м² застройки').font = f_norm
we.cell(row=r, column=6, value='=ROUND(TOTAL_SUM/AREA,0)').number_format = NUM; r += 2
we.cell(row=r, column=2, value='Не заполнены цены по выбранным позициям:').font = f_bold
we.cell(row=r, column=6, value=f'=SUMPRODUCT((C5:C{last}<>0)*(E5:E{last}=""))').number_format = NUM
we.cell(row=r, column=6).font = Font(name=F, size=10, bold=True, color='C00000')
r += 1
we.cell(row=r, column=2, value='Если не ноль — впишите цену в «Справочник», иначе позиция считается как 0.').font = f_note
we.freeze_panes = 'A5'

# ---------------------------------------------------------------- Сверка с П³
wv = wb.create_sheet('Сверка с П³')
title(wv, 'Сверка модели металла с конструктором П³ (76 вариантов)', 'Данные П³ сняты 18.11.2026 с публичного конструктора p3-platform.ru/constructor. Модель — те же правила, что в режиме «П³ (балки)».', 11)
hdr = ('L', 'B', 'H', 'Шаг', 'Уклон°', 'Снег', 'Стена мм', 'Кровля мм', 'МК П³, т', 'МК модель, т', 'Ошибка')
for i, h in enumerate(hdr, 1):
    c = wv.cell(row=4, column=i, value=h); c.font = Font(name=F, size=10, bold=True, color='FFFFFF'); c.fill = fill_h1
    wv.column_dimensions[get_column_letter(i)].width = 11
val = json.load(open(os.path.join(HERE, 'p3_sweep_summary.json')))
r = 5
for v in val:
    for i, k in enumerate(('L', 'Bw', 'H', 'step', 'slope', 'snow', 'wall', 'roof', 'p3', 'model'), 1):
        wv.cell(row=r, column=i, value=v[k]).font = f_norm
    wv.cell(row=r, column=11, value=f'=IF(I{r}=0,0,J{r}/I{r}-1)').number_format = '0.0%'
    r += 1
wv.cell(row=r + 1, column=1, value='Средняя абсолютная ошибка').font = f_bold
wv.cell(row=r + 1, column=11, value=f'=SUMPRODUCT(ABS(K5:K{r-1}))/COUNT(K5:K{r-1})').number_format = '0.0%'
wv.cell(row=r + 2, column=1, value='Ветер, грунт и нагрузка на пол на массу металла в П³ не влияют (проверено).').font = f_note

# ---------------------------------------------------------------- Методика
wm = wb.create_sheet('Методика')
title(wm, 'Методика и ограничения', None, 1)
wm.column_dimensions['A'].width = 130
text = [
    'Как устроен калькулятор',
    '• «Ввод» — параметры здания и комплектация. «Расчёт» — объёмы. «Смета» — стоимость. «Справочник» — профили, таблицы, цены.',
    '• Режим «П³ (балки)» повторяет правила конструктора П³, восстановленные по 76 моделям (метод «чёрного ящика», без доступа к коду). Точность массы металла: в среднем ≈ 1,4 %, 73 из 76 вариантов — в пределах 3 %.',
    '• Режим «КП (фермы)» повторяет конструкцию КП «Ангар 18 × 30 × 6»: рамы с фермами, прогоны П1, ригели стен, фахверк, нижний прогон-швеллер, без связей по кровле.',
    '',
    'Что восстановлено из П³',
    '• Рамы: число = ОКРУГЛ(L / шаг) + 1; колонны 40К1 длиной H + 0,3 м; стропила 2 на раму длиной (скат − 0,24 м), 55Б1 (45Б1 при пролёте ≤ 12 м и снеге ≤ 1 кПа).',
    '• Карнизные балки 30Б1 (шаг 7,5 м — 35Б1/40Б1) по обеим сторонам на всю длину.',
    '• Прогоны Z300 (Z250 при шаге ≤ 5 м); число рядов зависит от длины ската, снега и толщины кровельной панели.',
    '• Связи 20Б1: по стенам 4 шт на связевую панель, панелей = max(2; шагов/3); по кровле 2·ОКРВВЕРХ(шагов/2) на скат, вдвое больше при пролёте ≥ 21 м.',
    '• Ветер, тип грунта (кроме торфа) и нагрузка на пол на металл в П³ не влияют. Колонны 40К1 П³ не меняет ни при каких нагрузках.',
    '• Оболочка: стены = периметр × (H − 0,6) + фронтоны; кровля = 2·(L + 2)·(скат + 0,58); доборы и саморезы — по длинам примыканий (см. «Расчёт»).',
    '• Фундаменты: 4 анкера на колонну; объём фундамента растёт с грузовой площадью колонны; на торфе ×4. Плита пола: 150/180/220/260 мм при нагрузке до 0,75 / 2,5 / 4 / > 4 т/м².',
    '',
    'Что заметно в П³ (стоит обсудить с разработчиком)',
    '• Масса 40К1 в П³ — 72,6 кг/м, по сортаменту ≈ 138 кг/м: металл колонн занижен почти вдвое.',
    '• Фронтоны в площади стен учтены дважды (+ B²·tg α / 2 м²).',
    '• Нет фахверка на торцах при пролёте 18–36 м: торцевые панели без промежуточных опор.',
    '• Нет винтовых свай, пола из плит ПАГ, ферм, вертикальной раскладки панелей с ригелями.',
    '',
    'Ограничения',
    '• Это предварительный расчёт для КП. Окончательные сечения — по расчёту КМ и ИГИ.',
    '• Цены взяты из КП «Поколения» и пересчитаны к НДС 5 %; пустые цены надо заполнить.',
]
for i, t in enumerate(text, 3):
    c = wm.cell(row=i, column=1, value=t)
    c.font = f_bold if t and not t.startswith('•') else f_norm
    c.alignment = Alignment(wrap_text=True, vertical='top')

wb.save(OUT)
print('saved', OUT)
