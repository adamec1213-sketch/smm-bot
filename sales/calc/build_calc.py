"""Сборка Excel-калькулятора ангара «Поколения».

Правила расчёта металла, профилей, фундаментов и плиты — по коду публичного
конструктора П³ (разобран 18.11.2026) и проверены на 240 вариантах (лист «Сверка с П³»). Режим «КП (фермы)», сваи, пол из ПАГ и цены — из КП
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
    ('Нагрузки', None),
    ('SNOWREG', 'Снеговой район (СП 20.13330)', 'III', '', 'Москва и Санкт-Петербург — III. Другие города — по карте СП 20.13330 (прил. Е)'),
    ('SNOW_MAN', 'Снеговая нагрузка вручную, кПа (пусто = по району)', '', 'кПа', 'П³ считает только по этому числу; выбор района в П³ ни на что не влияет'),
    ('GAMMA', 'Коэффициент надёжности по нагрузке γf', 1.2, '', 'Как в П³ (по умолчанию 1,2)'),
    ('STEELGR', 'Марка стали', 'С255', '', 'С255 / С355 — меняет подбор профилей (как в П³)'),
    ('FLOORLOAD', 'Нагрузка на пол, т/м²', 1, 'т/м²', 'Для монолитной плиты (как в П³)'),
    ('Грунт (как в П³)', None),
    ('DATALEVEL', 'Данные о грунте', 'нет геологии', '', 'нет геологии — П³ берёт R = 180 кПа для любого грунта / основные данные / ИГИ'),
    ('SOILTYPE', 'Тип грунта', 'не знаю', '', 'Влияет, только если есть данные. Торф — всегда сваи'),
    ('SOILSTATE', 'Состояние грунта', 'неизвестно', '', 'плотный ×1,15 к R; рыхлый ×0,72 и плита +30 мм'),
    ('GW', 'Уровень грунтовых вод', 'неизвестно', '', 'менее 1 м: R ×0,78, щебень +50 мм; 1–3 м: R ×0,9'),
    ('SOILR', 'Расчётное сопротивление R по изысканиям, кПа (0 = по таблице)', 0, 'кПа', 'Работает только при «основные данные»/«ИГИ» И выбранном типе грунта (при «не знаю» П³ берёт 180)'),
    ('FROST', 'Глубина промерзания, м (0 = 1,4 м)', 0, 'м', 'Влияет только на высоту подколонника'),
    ('PILEDEPTH', 'Глубина несущего слоя для свай, м (0 = сваи 6 м)', 0, 'м', 'Если П³ уходит в сваи'),
    ('Конструкция', None),
    ('SCHEME', 'Схема каркаса', 'КП (фермы)', '', 'П³ (балки) — как конструктор П³; КП (фермы) — как КП 18×30'),
    ('FACHWERK', 'Фахверковые колонны на торцах', 'да', '', 'да / нет'),
    ('WALLLAYOUT', 'Раскладка стеновых панелей', 'вертикальная', '', 'горизонтальная (П³, без ригелей) / вертикальная (ригели стен, как КП)'),
    ('BASE', 'Основание стен', 'швеллер', '', 'цоколь (монолит 0,6 м, как П³) / швеллер (нижний прогон, как КП)'),
    ('COLMASS', 'Масса колонн 40К/50К', 'как в П³', '', 'как в П³ (40К1 = 72,6 кг/м — занижено) / по сечению (40К1 = 131,6 кг/м, по размерам из самого П³)'),
    ('NODEPCT', 'Узлы, пластины, болты, % от массы', 0.093, '%', 'КП 18×30: 2,4 т на 25,8 т = 9,3 %'),
    ('Оболочка', None),
    ('PANELTYPE', 'Утеплитель панелей', 'минвата', '', 'минвата / PIR'),
    ('WALLTHK', 'Толщина стеновых панелей, мм', 100, 'мм', '60–250'),
    ('ROOFTHK', 'Толщина кровельных панелей, мм', 120, 'мм', '80–250'),
    ('OVH_END', 'Свес кровли по торцам (с каждой стороны), м', '', 'м', 'Пусто = авто: П³ 1,0 м; КП 0,5 м'),
    ('OVH_EAVE', 'Свес кровли по карнизу, м (по скату)', '', 'м', 'Пусто = авто: П³ 0,58 м; КП 0'),
    ('Фундамент и пол', None),
    ('FOUND', 'Фундамент', 'винтовые сваи', '', 'монолит (столбчатые, как П³) / винтовые сваи (как КП) / плита-фундамент (плита пола работает как фундамент)'),
    ('PILESPERCOL', 'Свай под одну колонну, шт', 2, 'шт', 'КП: 2 сваи Ø133 с оголовком'),
    ('FLOOR', 'Пол', 'плиты ПАГ', '', 'монолитная плита (как П³) / плиты ПАГ (как КП) / нет'),
    ('Проёмы и опции', None),
    ('GATES', 'Ворота, шт', 0, 'шт', 'КП 18×30: не входят'),
    ('WINDOWS', 'Окна, м²', 0, 'м²', ''),
    ('DOORS', 'Двери, шт', 0, 'шт', 'Цена в справочнике пустая — заполните'),
    ('FLASH', 'Доборы и крепёж панелей включить в смету', 'нет', '', 'да / нет (КП 18×30: не входят)'),
    ('GUTTER', 'Водосток и снегозадержание', 'нет', '', 'да / нет'),
    ('DELIVERY', 'Доставка металла и панелей', 'нет', '', 'да / нет (КП 18×30: не входит)'),
    ('Объёмы из рабочей документации (если есть АР/КМ/КЖ — заполните, иначе пусто)', None),
    ('OVR_STEEL', 'Металл по КМ, т', '', 'т', 'Пусто = считает калькулятор. Заполнено = берётся из КМ (узлы уже внутри)'),
    ('OVR_WALL', 'Стеновые панели по АР, м²', '', 'м²', 'Пусто = по габаритам'),
    ('OVR_ROOF', 'Кровля по АР, м²', '', 'м²', 'Пусто = по габаритам'),
    ('OVR_SLAB', 'Бетон фундаментной плиты / пола по КЖ, м³', '', 'м³', 'Только при полу «монолитная плита»'),
    ('Коммерция', None),
    ('DESIGN', 'Проектирование (КЖ, КМ, геология), ₽', 420000, '₽', 'КП 18×30'),
    ('MARKUP', 'Наценка к итогу, %', 0, '%', 'Применяется ко всей смете'),
    ('VAT', 'Ставка НДС (цены в справочнике с НДС)', 0.05, '%', 'КП 18×30: НДС 5 %'),
]
r = 4
dv_lists = {
    'SNOWREG': '"I,II,III,IV,V,VI,VII,VIII"', 'STEELGR': '"С255,С355"',
    'DATALEVEL': '"нет геологии,основные данные,ИГИ"', 'SOILTYPE': '=SOIL_NAMES',
    'SOILSTATE': '"неизвестно,плотный,средней плотности,рыхлый"', 'GW': '"неизвестно,ниже 5 м,3–5 м,1–3 м,менее 1 м"',
    'COLMASS': '"как в П³,по сечению"', 'SCHEME': '"П³ (балки),КП (фермы)"', 'FACHWERK': '"да,нет"',
    'WALLLAYOUT': '"горизонтальная,вертикальная"', 'BASE': '"цоколь,швеллер"', 'PANELTYPE': '"минвата,PIR"',
    'FOUND': '"монолит,винтовые сваи,плита-фундамент"', 'FLOOR': '"монолитная плита,плиты ПАГ,нет"', 'FLASH': '"да,нет"',
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
    ('Колонна КП (К1)', 98.3, 'КП 18×30: 7 080 кг / 12 шт / 6 м'),
    ('Ферма КП, на 1 м пролёта', 62.2, 'КП 18×30: 6 720 кг / 6 шт / 18 м'),
    ('Прогон КП (П1)', 18.33, 'КП 18×30: 4 400 кг / 40 шт / 6 м'),
    ('Ригель стены КП (Ж1)', 14.67, 'КП 18×30: 4 224 кг / 288 м'),
    ('Фахверк КП (К2)', 40.0, 'КП 18×30: 1 040 кг / 4 шт / ~6,5 м'),
    ('Швеллер нижнего прогона', 12.5, 'КП 18×30: 1 200 кг / 96 м'),
    ('Связь стены КП (СВ1), кг/шт', 180, 'КП 18×30'),
]
for p, kg, src in profiles:
    ws[f'A{r}'] = p; ws[f'B{r}'] = kg; ws[f'B{r}'].font = f_in; ws[f'B{r}'].fill = fill_in; ws[f'B{r}'].number_format = '0.00'
    ws[f'E{r}'] = src; ws[f'E{r}'].font = f_note
    r += 1
prof_end = r - 1
wb.defined_names['PROF_NAMES'] = DefinedName('PROF_NAMES', attr_text=f"'Справочник'!$A${prof_start}:$A${prof_end}")
wb.defined_names['PROF_KG'] = DefinedName('PROF_KG', attr_text=f"'Справочник'!$B${prof_start}:$B${prof_end}")
r += 1

section(ws, r, 'Снеговые районы (СП 20.13330, вес снегового покрова Sg)', 5); r += 1
ws[f'A{r}'] = 'Район'; ws[f'B{r}'] = 'кПа'; ws[f'A{r}'].font = f_bold; ws[f'B{r}'].font = f_bold; r += 1
sn_start = r
for reg, kpa in (('I', 0.5), ('II', 1.0), ('III', 1.5), ('IV', 2.0), ('V', 2.5), ('VI', 3.0), ('VII', 3.5), ('VIII', 4.0)):
    ws[f'A{r}'] = reg; ws[f'B{r}'] = kpa; ws[f'B{r}'].font = f_in; ws[f'B{r}'].fill = fill_in
    ws[f'E{r}'] = {'III': 'Москва, Санкт-Петербург'}.get(reg, ''); ws[f'E{r}'].font = f_note
    r += 1
wb.defined_names['SN_REG'] = DefinedName('SN_REG', attr_text=f"'Справочник'!$A${sn_start}:$A${r-1}")
wb.defined_names['SN_KPA'] = DefinedName('SN_KPA', attr_text=f"'Справочник'!$B${sn_start}:$B${r-1}")
ws[f'A{r}'] = 'П³ подставляет число из поля «Снеговая нагрузка» как есть: нагрузка на кровлю = (снег + 0,32) × γf. Ветер в подборе не участвует.'; ws[f'A{r}'].font = f_note
r += 2

section(ws, r, 'Грунты: расчётное сопротивление R (таблица П³)', 5); r += 1
ws[f'A{r}'] = 'Грунт'; ws[f'B{r}'] = 'R, кПа'; ws[f'A{r}'].font = f_bold; ws[f'B{r}'].font = f_bold; r += 1
so_start = r
for nm, R in (('не знаю', 180), ('скальный', 800), ('крупнообломочный', 500), ('песок крупный', 420), ('песок средний', 300),
              ('песок мелкий', 210), ('песок пылеватый', 150), ('супесь', 180), ('суглинок', 200), ('глина', 240),
              ('насыпной', 120), ('торф', 60)):
    ws[f'A{r}'] = nm; ws[f'B{r}'] = R; ws[f'B{r}'].font = f_in; ws[f'B{r}'].fill = fill_in
    r += 1
wb.defined_names['SOIL_NAMES'] = DefinedName('SOIL_NAMES', attr_text=f"'Справочник'!$A${so_start}:$A${r-1}")
wb.defined_names['SOIL_RT'] = DefinedName('SOIL_RT', attr_text=f"'Справочник'!$B${so_start}:$B${r-1}")
ws[f'A{r}'] = 'Без геологии (или «не знаю») П³ всегда берёт R = 180 кПа, что бы ни было выбрано. Торф — всегда сваи.'; ws[f'A{r}'].font = f_note
r += 2

section(ws, r, 'Монолитная плита пола (таблица П³)', 5); r += 1
for h, c in zip(('Расч. нагрузка больше, кПа', 'Плита, мм', 'Песок, мм', 'Щебень, мм', 'Арматура', 'Ø, мм', 'Шаг, мм', 'Сеток'), 'ABCDEFGH'):
    ws[f'{c}{r}'] = h; ws[f'{c}{r}'].font = f_bold
r += 1
sl_start = r
for qd, t, sand, grav, d, sp, lay in ((0, 120, 100, 150, 10, 200, 1), (8, 150, 100, 150, 10, 150, 1), (15, 180, 120, 180, 12, 200, 2),
                                       (30, 220, 150, 200, 12, 150, 2), (50, 260, 180, 250, 14, 150, 2), (75, 300, 200, 300, 16, 150, 2),
                                       (105, 350, 220, 320, 16, 125, 2)):
    for c, v in zip('ABCDFGH', (qd, t, sand, grav, d, sp, lay)):
        ws[f'{c}{r}'] = v
        if c != 'A':
            ws[f'{c}{r}'].font = f_in; ws[f'{c}{r}'].fill = fill_in
    ws[f'E{r}'] = f'Ø{d}/{sp}, {lay} сет.'
    r += 1
for nm, col in (('SL_QD', 'A'), ('SL_T', 'B'), ('SL_SAND', 'C'), ('SL_GRAV', 'D'), ('SL_D', 'F'), ('SL_S', 'G'), ('SL_LAY', 'H')):
    wb.defined_names[nm] = DefinedName(nm, attr_text=f"'Справочник'!${col}${sl_start}:${col}${r-1}")
ws[f'A{r}'] = 'Расчётная нагрузка = (нагрузка на пол × 10 + вес плиты) × γf. Насыпной/рыхлый грунт: +30 мм плиты, +50 песка, +50 щебня; торф: +60/+80/+80; вода < 1 м: щебень +50.'; ws[f'A{r}'].font = f_note
r += 2

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
    ('P_BORED', 'Буронабивная свая (если П³ уходит в сваи)', '', 'шт', 'Нет данных — впишите'),
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


sec('Нагрузки')
row('SNOW', 'Снеговая нагрузка, кПа', '=IF(SNOW_MAN="",INDEX(SN_KPA,MATCH(SNOWREG,SN_REG,0)),SNOW_MAN)', 'кПа', 'По району или вручную')
row('SNOW_C', 'Снег в расчёте П³ (не меньше 0,5), кПа', '=MAX(0.5,SNOW)', 'кПа', 'П³: max(0,5; снег)')
row('ROOFQ', 'Расчётная нагрузка на кровлю, кПа', '=(SNOW_C+0.32)*GAMMA', 'кПа', 'П³: (снег + 0,32 собственный вес) × γf')
row('FY', 'Расчётное сопротивление стали, МПа', '=IF(STEELGR="С355",355,255)', 'МПа', 'П³: С255 → 255, С355 → 355', NUM)

sec('Геометрия')
row('IS_P3', 'Режим П³ (1) / КП (0)', '=IF(SCHEME="П³ (балки)",1,0)', '', '', NUM)
row('NB', 'Число шагов рам', '=MAX(1,ROUND(L/STEP,0))', 'шт', 'П³: рам = шагов + 1', NUM)
row('FRAMES', 'Число рам', '=NB+1', 'шт', '', NUM)
row('STEP_A', 'Фактический шаг рам, м', '=L/NB', 'м', 'П³ делит длину на равные шаги')
row('ALPHA', 'Уклон, рад', '=RADIANS(SLOPE)', '', '')
row('LS', 'Длина ската, м', '=B/2/COS(ALPHA)', 'м', '')
row('PER', 'Периметр, м', '=2*(L+B)', 'м', '')
row('AREA', 'Площадь застройки, м²', '=L*B', 'м²', '')
row('PLINTH_H', 'Высота цоколя, м', '=IF(BASE="цоколь",0.6,0)', 'м', 'П³: монолитный цоколь 0,6 м; панели начинаются над ним')
row('OVH_E', 'Свес по торцам, м', '=IF(OVH_END="",IF(IS_P3=1,1,0.5),OVH_END)', 'м', 'П³: кровля длиннее здания на 2 м; КП: на 1 м')
row('OVH_V', 'Свес по карнизу (по скату), м', '=IF(OVH_EAVE="",IF(IS_P3=1,0.58,0),OVH_EAVE)', 'м', 'П³: +0,58 м к скату')
row('FACH_N', 'Колонн фахверка (оба торца)', '=IF(FACHWERK="да",2*MAX(0,ROUND(B/6,0)-1),0)', 'шт', 'КП 18×30: 4 шт при пролёте 18 м', NUM)

sec('Прогоны (как в П³)')
row('PBS', 'Допустимый пролёт кровельной панели, м', '=IF(PANELTYPE="PIR",IF(ROOFTHK<=80,1.8,IF(ROOFTHK<=100,2.2,IF(ROOFTHK<=120,2.5,IF(ROOFTHK<=150,2.8,3)))),IF(ROOFTHK<=80,1.25,IF(ROOFTHK<=100,1.5,IF(ROOFTHK<=120,1.75,IF(ROOFTHK<=150,2.05,2.35)))))', 'м', 'Таблица П³ по типу и толщине панели')
row('PURL_STEP', 'Шаг прогонов, м', '=MAX(0.9,MIN(2.8,ROUNDDOWN(PBS*SQRT(1.8/MAX(1,SNOW_C+0.25))*10,0)/10))', 'м', 'П³: пролёт панели × √(1,8 / (снег + 0,25)), от 0,9 до 2,8 м, вниз до 0,1 м')
row('PR_N0', 'Рядов прогонов от карниза с шагом (по горизонтали)', '=INT((B+0.001)/PURL_STEP)+1', 'шт', 'П³ раскладывает прогоны по горизонтальной проекции', NUM)
row('PR_K', 'Номер ряда у конька', '=ROUND(B/2/PURL_STEP,0)', '', '', NUM)
row('PURL_ROWS', 'Рядов прогонов', '=IF(IS_P3=1,PR_N0+IF(B/2-(-B/2+(PR_N0-1)*PURL_STEP)>0.01,1,0)+IF(AND(PR_K<=PR_N0-1,ABS(B/2-PR_K*PURL_STEP)<0.05),0,1),2*ROUNDUP(LS/2.5,0))', 'шт', 'П³: ряды с шагом + ряд у карниза + ряд у конька. КП: 4 ряда на скат при скате 9 м', NUM)
row('PURL_PCS', 'Прогонов, шт', '=PURL_ROWS*NB', 'шт', '', NUM)

sec('Металлоконструкции')
row('COLS', 'Колонны рам, шт', '=2*FRAMES', 'шт', 'П³ и КП', NUM)
row('COL_KGM', 'Масса 1 м колонны П³, кг', "=IF(COLMASS=\"по сечению\",INDEX(P3_KGR,MATCH(COL_PROF,P3_NAMES,0)),INDEX(P3_KG,MATCH(COL_PROF,P3_NAMES,0)))", 'кг/м', 'См. «Подбор П³»', NUM1)
row('COL_KG', 'Колонны рам, кг', '=IF(IS_P3=1,COLS*(H+0.0285+INDEX(P3_H,MATCH(RAF_PROF,P3_NAMES,0))/2)*COL_KGM,COLS*H*INDEX(PROF_KG,MATCH("Колонна КП (К1)",PROF_NAMES,0)))', 'кг', 'П³: длина = H + высота стропила / 2 + 0,03 м. КП: 98,3 кг/м', NUM)
row('RAF_KG', 'Стропильные балки / фермы, кг', '=IF(IS_P3=1,2*FRAMES*(LS-0.24)*INDEX(P3_KG,MATCH(RAF_PROF,P3_NAMES,0)),FRAMES*B*INDEX(PROF_KG,MATCH("Ферма КП, на 1 м пролёта",PROF_NAMES,0)))', 'кг', 'П³: 2 балки на раму длиной (скат − 0,24 м). КП: ферма 62,2 кг на 1 м пролёта', NUM)
row('EDGE_KG', 'Карнизные балки, кг', '=IF(IS_P3=1,2*L*INDEX(P3_KG,MATCH(EDGE_PROF,P3_NAMES,0)),0)', 'кг', 'П³: 2 линии на всю длину. В КП карнизный прогон входит в прогоны', NUM)
row('PURL_KG', 'Прогоны, кг', '=PURL_ROWS*L*IF(IS_P3=1,INDEX(P3_KG,MATCH(PURL_PROF,P3_NAMES,0)),INDEX(PROF_KG,MATCH("Прогон КП (П1)",PROF_NAMES,0)))', 'кг', '', NUM)
row('BRW_I0', 'Первая доп. связевая панель (П³)', '=MAX(3,ROUNDUP(30/STEP_A-0.000001,0))', '', 'П³: связи в крайних панелях + через 3 панели после 30 м', NUM)
row('BRW_PCS', 'Связи по стенам, шт', '=IF(IS_P3=1,4*(MIN(2,NB)+IF(NB-2>=BRW_I0,INT((NB-2-BRW_I0)/3)+1,0)),4*MAX(1,ROUNDUP(NB/5,0)))', 'шт', 'П³: крест (2 шт) на каждой стене в каждой связевой панели. КП: 4 шт на 30 м', NUM)
row('BRW_KG', 'Связи по стенам, кг', '=IF(IS_P3=1,BRW_PCS*SQRT(STEP_A^2+(H-MIN(0.75,0.16*H))^2)*INDEX(P3_KG,MATCH("20Б1",P3_NAMES,0)),BRW_PCS*INDEX(PROF_KG,MATCH("Связь стены КП (СВ1), кг/шт",PROF_NAMES,0)))', 'кг', 'П³: 20Б1 по диагонали панели от отметки min(0,75; 0,16H). КП: СВ1 180 кг/шт', NUM)
row('BRR_PCS', 'Связи по кровле, диагоналей на скат', '=IF(IS_P3=1,2*ROUNDUP(NB/2,0),0)', 'шт', 'П³: крест в каждой второй панели (1-й, 3-й, …) на каждом скате; диагонали > 12 м режутся на части', NUM)
row('BRR_KG', 'Связи по кровле, кг', '=2*BRR_PCS*SQRT(STEP_A^2+LS^2)*INDEX(P3_KG,MATCH("20Б1",P3_NAMES,0))', 'кг', 'П³: 20Б1, оба ската', NUM)
row('KNEE_KG', 'Укосины торцевых стен, кг', '=IF(IS_P3=1,0,4*104)', 'кг', 'КП: УК1 4 × 104 кг', NUM)
row('FACH_KG', 'Фахверк, кг', '=FACH_N*(H+B/4*TAN(ALPHA))*INDEX(PROF_KG,MATCH("Фахверк КП (К2)",PROF_NAMES,0))', 'кг', 'КП', NUM)
row('GIRT_ROWS', 'Рядов ригелей стен', '=IF(WALLLAYOUT="вертикальная",ROUNDUP(H/2,0),0)', 'шт', 'КП: 3 ряда при H = 6 м', NUM)
row('GIRT_KG', 'Ригели стен, кг', '=GIRT_ROWS*PER*INDEX(PROF_KG,MATCH("Ригель стены КП (Ж1)",PROF_NAMES,0))', 'кг', 'КП', NUM)
row('CHAN_KG', 'Нижний прогон-швеллер, кг', '=IF(BASE="швеллер",PER*INDEX(PROF_KG,MATCH("Швеллер нижнего прогона",PROF_NAMES,0)),0)', 'кг', 'КП', NUM)
row('STEEL_NET', 'Итого элементы, кг', '=COL_KG+RAF_KG+EDGE_KG+PURL_KG+BRW_KG+BRR_KG+KNEE_KG+FACH_KG+GIRT_KG+CHAN_KG', 'кг', '', NUM)
row('NODE_KG', 'Узлы, пластины, болты, кг', '=STEEL_NET*NODEPCT', 'кг', 'П³ не даёт массу пластин; % из КП', NUM)
row('STEEL_T', 'МЕТАЛЛОКОНСТРУКЦИИ ВСЕГО, т', '=IF(OVR_STEEL<>"",OVR_STEEL,ROUND((STEEL_NET+NODE_KG)/1000,1))', 'т', 'Если заполнен «Металл по КМ» — берётся он', NUM1)
row('STEEL_KG_P3', 'Масса «как в П³» (без узлов), кг', '=COL_KG+RAF_KG+EDGE_KG+PURL_KG+BRW_KG+BRR_KG', 'кг', 'Совпадает с полем «МК» в П³ (режим П³, масса колонн «как в П³»)', NUM)
row('STEEL_T_P3', 'Для сверки: масса «как в П³», т', '=ROUND(STEEL_KG_P3/1000,2)', 'т', '', NUM2)
row('STEEL_KGM2', 'Металлоёмкость, кг/м²', '=STEEL_T*1000/AREA', 'кг/м²', '', NUM1)
row('K_MAX', 'Макс. коэффициент использования (П³)', "=KMAX_P3", '', 'Больше 1 — профиль из библиотеки П³ не проходит', NUM2)

sec('Оболочка (сэндвич-панели)')
row('WALL_M2', 'Стеновые панели, м²', '=IF(OVR_WALL<>"",OVR_WALL,ROUND(PER*(H-PLINTH_H)+B^2*TAN(ALPHA)/2,0))', 'м²', 'Геометрия: стены + 2 фронтона. В П³ фронтоны учтены дважды (+B²·tg α/2)')
row('ROOF_M2', 'Кровельные панели, м²', '=IF(OVR_ROOF<>"",OVR_ROOF,ROUND(2*(L+2*OVH_E)*(LS+OVH_V),0))', 'м²', 'П³: 2·(L+2)·(скат+0,58); КП: 2·(L+1)·скат')
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

sec('Грунт (как в П³)')
row('R_TAB', 'R по таблице грунтов, кПа', '=INDEX(SOIL_RT,MATCH(SOILTYPE,SOIL_NAMES,0))', 'кПа', 'Справочник', NUM)
row('R_CALC', 'R с поправками, кПа', '=IF(SOILR>0,SOILR,R_TAB*IF(SOILSTATE="плотный",1.15,IF(SOILSTATE="рыхлый",0.72,1))*IF(GW="менее 1 м",0.78,IF(GW="1–3 м",0.9,1)))', 'кПа', 'П³: плотный ×1,15; рыхлый ×0,72; вода < 1 м ×0,78; 1–3 м ×0,9', NUM)
row('R_GR', 'Принятое R, кПа', '=IF(OR(DATALEVEL="нет геологии",SOILTYPE="не знаю"),180,ROUND(R_CALC,0))', 'кПа', 'П³: без геологии всегда 180 кПа', NUM)
row('WEAK', 'Слабый грунт (сваи обязательно)', '=IF(OR(SOILTYPE="торф",R_GR<95,AND(SOILTYPE="насыпной",GW="менее 1 м")),1,0)', '', 'П³: торф, R < 95 кПа, насыпной с водой < 1 м', NUM)
row('FROST_D', 'Глубина промерзания в расчёте, м', '=IF(FROST>0,FROST,1.4)', 'м', '')
row('PILE_L', 'Длина сваи, м', '=IF(PILEDEPTH>0,MAX(3,PILEDEPTH),6)', 'м', 'П³')

sec('Фундаменты')
row('COLS_ALL', 'Колонн всего (с фахверком)', '=COLS+FACH_N', 'шт', '', NUM)
row('PILES', 'Винтовых свай, шт', '=IF(FOUND="винтовые сваи",COLS_ALL*PILESPERCOL,0)', 'шт', 'КП: 2 сваи под колонну', NUM)
row('FOOT_N', 'Монолитных фундаментов (ростверков), шт', "=IF(FOUND=\"монолит\",COLS,0)", 'шт', 'П³: под каждую колонну рамы; под фахверк — нет', NUM)
row('FOOT_TYPE', 'Тип фундамента по П³', "=FT_TYPE", '', 'Подбор по реакции колонны: см. «Подбор П³»', '@')
row('FOOT_V', 'Бетон фундаментов, м³', "=IF(FOUND=\"монолит\",FT_CONC,0)", 'м³', 'П³: плита + подколонник (+ сваи)')
row('FOOT_REBAR', 'Арматура фундаментов, кг', "=IF(FOUND=\"монолит\",FT_REB,0)", 'кг', 'П³: 95 кг/м³, на сваях 125 кг/м³', NUM)
row('ANCHORS', 'Анкерные болты, шт', "=IF(FOUND=\"монолит\",FT_ANC,0)", 'шт', 'П³: 4 / 8 / 12 на колонну по реакции', NUM)
row('BORED_N', 'Буронабивных свай, шт', "=IF(FOUND=\"монолит\",FT_PILES,0)", 'шт', 'Только если П³ уходит в сваи (торф, слабый грунт, большие реакции)', NUM)

sec('Цоколь (если выбран)')
row('PL_CONC', 'Бетон цоколя B25, м³', '=IF(BASE="цоколь",PER*0.6*0.2,0)', 'м³', 'П³: 0,6 × 0,2 м по периметру')
row('PL_REBAR', 'Арматура цоколя, кг', '=PL_CONC*110', 'кг', 'П³: 110 кг/м³', NUM)
row('PL_XPS', 'ПЕНОПЛЭКС цоколя 50 мм, м²', '=IF(BASE="цоколь",PER*0.6,0)', 'м²', 'П³')
row('PL_WP', 'Гидроизоляция цоколя, м²', '=IF(BASE="цоколь",PER*0.8,0)', 'м²', 'П³')
row('PL_FORM', 'Опалубка цоколя, м²', '=IF(BASE="цоколь",2*PER*0.6,0)', 'м²', 'П³')

sec('Пол')
row('SL_Q', 'Нагрузка на пол, кПа', '=FLOORLOAD*10', 'кПа', '1 т/м² = 10 кПа')
row('SL_I1', 'Строка таблицы (1-й проход)', '=MATCH((SL_Q+25*0.12)*GAMMA-0.000001,SL_QD,1)', '', 'П³ подбирает толщину в два прохода с учётом веса плиты', NUM)
row('SL_I', 'Строка таблицы плиты', '=MAX(SL_I1,MATCH((SL_Q+25*INDEX(SL_T,SL_I1)/1000)*GAMMA-0.000001,SL_QD,1))', '', '', NUM)
row('SL_ADD', 'Надбавка за грунт (насыпной/рыхлый 1, торф 2)', '=IF(SOILTYPE="торф",2,IF(OR(SOILTYPE="насыпной",SOILSTATE="рыхлый"),1,0))', '', '', NUM)
row('SLAB_T', 'Толщина монолитной плиты, мм', '=IF(FLOOR="монолитная плита",MIN(400,INDEX(SL_T,SL_I)+IF(SL_ADD=2,60,IF(SL_ADD=1,30,0))),0)', 'мм', 'П³', NUM)
row('SLAB_V', 'Бетон плиты B25, м³', '=IF(AND(SLAB_T>0,OVR_SLAB<>""),OVR_SLAB,AREA*SLAB_T/1000)', 'м³', 'Если заполнен бетон по КЖ — берётся он')
row('SLAB_REBAR', 'Арматура плиты, кг', '=IF(SLAB_T>0,AREA*INDEX(SL_LAY,SL_I)*2*(1000/INDEX(SL_S,SL_I))*0.00617*INDEX(SL_D,SL_I)^2*1.05,0)', 'кг', 'П³: сетки в 2 направлениях + 5 % на нахлёст', NUM)
row('SLAB_SAND', 'Песок на подушку, м³', '=IF(SLAB_T>0,AREA*MIN(400,INDEX(SL_SAND,SL_I)+IF(SL_ADD=2,80,IF(SL_ADD=1,50,0)))/1000*1.15,0)', 'м³', 'П³: с запасом 15 %')
row('SLAB_GRAV', 'Щебень на подушку, м³', '=IF(SLAB_T>0,AREA*MIN(500,INDEX(SL_GRAV,SL_I)+IF(SL_ADD=2,80,IF(SL_ADD=1,50,0))+IF(GW="менее 1 м",50,0))/1000*1.12,0)', 'м³', 'П³: с запасом 12 %')
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

# ---------------------------------------------------------------- Подбор П³
wp = wb.create_sheet('Подбор П³')
title(wp, 'Подбор профилей и фундаментов — точная копия алгоритма П³',
      'Формулы взяты из кода конструктора П³ (18.11.2026) и проверены на 240 вариантах: профили, коэффициенты и фундаменты совпали во всех.', 11)
for col, w in zip('ABCDEFGHIJK', (30, 11, 11, 11, 11, 11, 12, 12, 12, 12, 40)):
    wp.column_dimensions[col].width = w
r = 4
section(wp, r, 'Библиотека профилей П³ (размеры в м)', 11); r += 1
for i, h in enumerate(('Профиль', 'h', 'b', 'tw', 'tf', 'кг/м в П³', 'A, м²', 'I, м⁴', 'W, м³', 'кг/м по сечению'), 1):
    wp.cell(row=r, column=i, value=h).font = f_bold
r += 1
p3_start = r
P3P = [('40К1', .393, .400, .011, .016, 72.6), ('40К2', .400, .400, .013, .020, 88.6), ('50К1', .492, .400, .012, .020, 92.4),
       ('50К2', .500, .400, .014, .024, 110.8), ('40Б1', .392, .199, .007, .011, 48.1), ('45Б1', .443, .199, .008, .012, 59.8),
       ('50Б1', .492, .199, .0088, .014, 73.0), ('55Б1', .543, .220, .009, .014, 82.5), ('20Б1', .200, .100, .0056, .0085, 21.3),
       ('30Б1', .296, .140, .0058, .0085, 32.9), ('35Б1', .346, .155, .0062, .0085, 38.9), ('Z250', .25, .07, .003, .003, 8.8),
       ('Z300', .30, .08, .0035, .0035, 11.5)]
for nm, h, b_, tw, tf, kg in P3P:
    wp.cell(row=r, column=1, value=nm)
    for c, v in zip(range(2, 7), (h, b_, tw, tf, kg)):
        wp.cell(row=r, column=c, value=v).font = f_in
    wp.cell(row=r, column=7, value=f'=2*C{r}*E{r}+(B{r}-2*E{r})*D{r}').number_format = '0.000000'
    wp.cell(row=r, column=8, value=f'=2*(C{r}*E{r}^3/12+C{r}*E{r}*(B{r}/2-E{r}/2)^2)+D{r}*MAX(0.001,B{r}-2*E{r})^3/12').number_format = '0.000E+00'
    wp.cell(row=r, column=9, value=f'=H{r}/(B{r}/2)').number_format = '0.000E+00'
    wp.cell(row=r, column=10, value=f'=G{r}*7850').number_format = '0.0'
    r += 1
for nm, col in (('P3_NAMES', 'A'), ('P3_H', 'B'), ('P3_KG', 'F'), ('P3_A', 'G'), ('P3_I', 'H'), ('P3_W', 'I'), ('P3_KGR', 'J')):
    wb.defined_names[nm] = DefinedName(nm, attr_text=f"'Подбор П³'!${col}${p3_start}:${col}${r-1}")
wp.cell(row=r, column=1, value='Колонны 40К–50К: П³ считает прочность по реальному сечению (столбец A), а массу берёт заниженную (кг/м в П³). Пример: 40К1 — 72,6 вместо 131,6 кг/м.').font = f_note
r += 2

def lk(col, cell):
    return f'INDEX({col},MATCH({cell},P3_NAMES,0))'

def beam_block(key, label, cands, Lx, qx, lim, note):
    global r
    section(wp, r, label, 11); r += 1
    wp.cell(row=r, column=1, value='Пролёт L, м'); wp.cell(row=r, column=2, value=Lx).number_format = NUM2
    wp.cell(row=r, column=3, value='q, кН/м'); wp.cell(row=r, column=4, value=qx).number_format = NUM2
    wp.cell(row=r, column=5, value='Прогиб ≤ L/'); wp.cell(row=r, column=6, value=lim)
    wp.cell(row=r, column=11, value=note).font = f_note
    rl = r; r += 1
    for i, h in enumerate(('Кандидат', 'M, кН·м', 'σ / Ry', 'f, мм', 'f / [f]', 'k', 'проходит (k ≤ 0,88)'), 1):
        wp.cell(row=r, column=i, value=h).font = f_bold
    r += 1
    c0 = r
    for c in cands:
        wp.cell(row=r, column=1, value=c)
        wp.cell(row=r, column=2, value=f'=$D${rl}*$B${rl}^2/8').number_format = NUM2
        wp.cell(row=r, column=3, value=f'=B{r}*1000/({lk("P3_W", f"A{r}")}*FY*1000000)').number_format = NUM2
        wp.cell(row=r, column=4, value=f'=5*$D${rl}*1000*$B${rl}^4/(384*205000000000*{lk("P3_I", f"A{r}")})*1000').number_format = NUM1
        wp.cell(row=r, column=5, value=f'=D{r}/1000/($B${rl}/$F${rl})').number_format = NUM2
        wp.cell(row=r, column=6, value=f'=MAX(C{r},E{r})').number_format = NUM2
        wp.cell(row=r, column=7, value=f'=IF(F{r}<=0.88,1,0)')
        r += 1
    c1 = r - 1
    wp.cell(row=r, column=1, value='Принято').font = f_bold
    pc = wp.cell(row=r, column=2, value=f'=IFERROR(INDEX(A{c0}:A{c1},MATCH(1,G{c0}:G{c1},0)),IF(MIN(F{c0}:F{c1})<9,INDEX(A{c0}:A{c1},MATCH(MIN(F{c0}:F{c1}),F{c0}:F{c1},0)),A{c1}))')
    pc.font = f_bold
    wp.cell(row=r, column=3, value='k =').font = f_bold
    kc = wp.cell(row=r, column=4, value=f'=IFERROR(INDEX(F{c0}:F{c1},MATCH(1,G{c0}:G{c1},0)),MIN(9,MIN(F{c0}:F{c1})))')
    kc.number_format = NUM2; kc.font = f_bold
    wp.cell(row=r, column=5, value=f'=IF(D{r}<=1,"проходит","НЕ ПРОХОДИТ: в библиотеке П³ нет профиля мощнее")').font = f_bold
    name(key + '_PROF', 'Подбор П³', f'B{r}'); name(key + '_K', 'Подбор П³', f'D{r}')
    r += 2

beam_block('RAF', 'Стропильная балка (П³ считает как простую балку на весь пролёт B)', ['40Б1', '45Б1', '50Б1', '55Б1'],
           '=B', '=ROOFQ*STEP_A', 220, 'П³: q = нагрузка на кровлю × шаг рам. Рамная работа (жёсткие узлы) не учитывается')
beam_block('PURL', 'Прогон', ['Z250', 'Z300'], '=STEP_A', '=ROOFQ*PURL_STEP', 200, 'П³: пролёт = шаг рам, грузовая ширина = шаг прогонов')
beam_block('EDGE', 'Карнизная (периметральная) балка', ['30Б1', '35Б1', '40Б1', '45Б1', '50Б1'],
           '=STEP_A', '=ROOFQ*MAX(1.5,MIN(4,MIN(B/2,2*PURL_STEP)))', 250, 'П³: грузовая ширина = min(B/2; 2 шага прогонов), от 1,5 до 4 м')

section(wp, r, 'Колонна (П³ проверяет только сжатие с устойчивостью, без изгиба от ветра и рамы)', 11); r += 1
wp.cell(row=r, column=1, value='N, кН'); wp.cell(row=r, column=2, value='=STEP_A*B*ROOFQ*1.08').number_format = NUM1
wp.cell(row=r, column=3, value='Высота, м'); wp.cell(row=r, column=4, value='=H')
wp.cell(row=r, column=11, value='П³: N = шаг × ВЕСЬ пролёт × нагрузка × 1,08').font = f_note
rl = r; r += 1
for i, h in enumerate(('Кандидат', 'i, м', 'λ', 'φ', 'Несущая, кН', 'k', 'проходит (k ≤ 0,82)'), 1):
    wp.cell(row=r, column=i, value=h).font = f_bold
r += 1
c0 = r
for c in ['40К1', '40К2', '50К1', '50К2']:
    wp.cell(row=r, column=1, value=c)
    wp.cell(row=r, column=2, value=f'=SQRT({lk("P3_I", f"A{r}")}/{lk("P3_A", f"A{r}")})').number_format = '0.000'
    wp.cell(row=r, column=3, value=f'=$D${rl}/MAX(0.015,B{r})').number_format = NUM1
    wp.cell(row=r, column=4, value=f'=MAX(0.35,MIN(0.95,1-C{r}/420))').number_format = NUM2
    wp.cell(row=r, column=5, value=f'={lk("P3_A", f"A{r}")}*FY*1000000*D{r}/1000').number_format = NUM
    wp.cell(row=r, column=6, value=f'=$B${rl}/MAX(1,E{r})').number_format = NUM2
    wp.cell(row=r, column=7, value=f'=IF(F{r}<=0.82,1,0)')
    r += 1
c1 = r - 1
wp.cell(row=r, column=1, value='Принято').font = f_bold
wp.cell(row=r, column=2, value=f'=IFERROR(INDEX(A{c0}:A{c1},MATCH(1,G{c0}:G{c1},0)),IF(MIN(F{c0}:F{c1})<9,INDEX(A{c0}:A{c1},MATCH(MIN(F{c0}:F{c1}),F{c0}:F{c1},0)),A{c1}))').font = f_bold
wp.cell(row=r, column=3, value='k =').font = f_bold
wp.cell(row=r, column=4, value=f'=IFERROR(INDEX(F{c0}:F{c1},MATCH(1,G{c0}:G{c1},0)),MIN(9,MIN(F{c0}:F{c1})))').number_format = NUM2
name('COL_PROF', 'Подбор П³', f'B{r}'); name('COL_K', 'Подбор П³', f'D{r}')
r += 2
wp.cell(row=r, column=1, value='Макс. коэффициент использования').font = f_bold
kc = wp.cell(row=r, column=2, value='=MAX(RAF_K,PURL_K,EDGE_K,COL_K)'); kc.number_format = NUM2; kc.font = Font(name=F, size=12, bold=True, color='C00000')
wp.cell(row=r, column=3, value='=IF(B{0}<=0.9,"П³ показал бы: проходит внутренние проверки","П³ показал бы: есть элементы с k выше целевого — нужен расчёт КМ")'.format(r)).font = f_bold
name('KMAX_P3', 'Подбор П³', f'B{r}')
r += 1
wp.cell(row=r, column=1, value='Если k > 1, П³ всё равно выдаёт массу металла по самому мощному профилю библиотеки: реальная конструкция будет тяжелее.').font = f_note
r += 2

section(wp, r, 'Фундаменты под колонны рам (алгоритм П³)', 11); r += 1
wp.cell(row=r, column=1, value='Масса металла для нагрузки, кг'); wp.cell(row=r, column=2, value='=IF(IS_P3=1,STEEL_KG_P3,STEEL_NET)').number_format = NUM
wp.cell(row=r, column=3, value='Стены, кН'); wp.cell(row=r, column=4, value='=PER*H*0.16').number_format = NUM1
wp.cell(row=r, column=11, value='П³: вес стен 0,16 кПа, кровли 0,35 кПа; снег без γf; итог × 1,2').font = f_note
rs = r; r += 1
wp.cell(row=r, column=2, value='Крайние рамы').font = f_bold; wp.cell(row=r, column=3, value='Средние рамы').font = f_bold
r += 1
rows_f = [
    ('cnt', 'Колонн, шт', '=IF(NB>=1,4,0)', '=2*(NB-1)', NUM),
    ('ta', 'Грузовая площадь, м²', '=STEP_A/2*B/2', '=STEP_A*B/2', NUM2),
    ('N', 'Реакция N, кН', '=({c}{ta}*(SNOW_C+0.35)+($B${rs}*9.81/1000+$D${rs})*{c}{ta}/AREA)*1.2', None, NUM1),
    ('req', 'Нужная площадь подошвы, м²', '={c}{N}*1.25/MAX(70,R_GR)', None, NUM2),
    ('pile', 'Сваи? (1 = да)', '=IF(OR(WEAK=1,{c}{req}>9,AND({c}{N}>1700,R_GR<180)),1,0)', None, NUM),
    ('pc', 'Свай в кусте, шт', '=IF({c}{pile}=1,IF({c}{N}<850,4,IF({c}{N}<1450,6,9)),0)', None, NUM),
    ('pd', 'Диаметр сваи, м', '=IF({c}{pile}=1,IF({c}{N}<1200,0.3,0.4),0)', None, NUM2),
    ('side', 'Подошва / ростверк, сторона, м', '=IF({c}{pile}=1,IF({c}{pc}<=4,1.9,IF({c}{pc}<=6,2.4,3)),MIN(4,MAX(1.1,ROUNDUP(SQRT(MAX(1,{c}{req}))/0.1-0.000000001,0)*0.1)))', None, NUM2),
    ('thk', 'Толщина плиты, м', '=IF({c}{pile}=1,MIN(1,MAX(0.6,0.55+{c}{N}/5000)),MIN(0.9,MAX(0.45,ROUNDUP((0.38+{c}{side}*0.09)/0.05-0.000000001,0)*0.05)))', None, NUM2),
    ('ped', 'Подколонник, сторона, м', '=IF({c}{pile}=1,MIN(1,MAX(0.6,0.55+{c}{N}/4500)),MIN(1,MAX(0.55,ROUNDUP((0.5+{c}{N}/5000)/0.05-0.000000001,0)*0.05)))', None, NUM2),
    ('pedH', 'Подколонник, высота, м', '=IF({c}{pile}=1,0.55,MIN(1.1,MAX(0.45,FROST_D-{c}{thk}+0.15)))', None, NUM2),
    ('conc', 'Бетон на 1 фундамент, м³', '={c}{side}^2*{c}{thk}+{c}{ped}^2*{c}{pedH}+{c}{pc}*PI()*({c}{pd}/2)^2*PILE_L', None, '0.000'),
    ('reb', 'Арматура на 1 фундамент, кг', '={c}{conc}*IF({c}{pile}=1,125,95)', None, NUM),
    ('anc', 'Анкеров на колонну, шт', '=IF({c}{N}<700,4,IF({c}{N}<1500,8,12))', None, NUM),
    ('ancd', 'Диаметр анкера, мм', '=IF({c}{N}<700,24,IF({c}{N}<1500,30,36))', None, NUM),
]
pos = {'rs': rs}
for key, lab, fb, fc, fmt in rows_f:
    pos[key] = r
    wp.cell(row=r, column=1, value=lab)
    for c, f in (('B', fb), ('C', fc if fc else fb)):
        ff = f.replace('{c}', c)
        for k2, rr in pos.items():
            ff = ff.replace('{' + k2 + '}', str(rr))
        wp[f'{c}{r}'] = ff
        wp[f'{c}{r}'].number_format = fmt
    r += 1
r += 1
P = pos
tot = [('FT_CONC', 'Бетон всего, м³', f'=B{P["cnt"]}*B{P["conc"]}+C{P["cnt"]}*C{P["conc"]}', NUM1),
       ('FT_REB', 'Арматура всего, кг', f'=B{P["cnt"]}*B{P["reb"]}+C{P["cnt"]}*C{P["reb"]}', NUM),
       ('FT_ANC', 'Анкеров всего, шт', f'=B{P["cnt"]}*B{P["anc"]}+C{P["cnt"]}*C{P["anc"]}', NUM),
       ('FT_PILES', 'Свай всего, шт', f'=B{P["cnt"]}*B{P["pc"]}+C{P["cnt"]}*C{P["pc"]}', NUM),
       ('FT_TYPE', 'Тип', f'=IF(B{P["pile"]}+C{P["pile"]}=0,"отдельные монолитные "&TEXT(B{P["side"]},"0.0")&"×"&TEXT(B{P["side"]},"0.0")&" и "&TEXT(C{P["side"]},"0.0")&"×"&TEXT(C{P["side"]},"0.0")&" м","свайно-ростверковый: сваи Ø"&TEXT(MAX(B{P["pd"]},C{P["pd"]})*1000,"0")&" мм, L = "&TEXT(PILE_L,"0.0")&" м")', '@')]
for key, lab, f, fmt in tot:
    wp.cell(row=r, column=1, value=lab).font = f_bold
    c = wp.cell(row=r, column=2, value=f); c.number_format = fmt; c.font = f_bold
    name(key, 'Подбор П³', f'B{r}')
    r += 1
wp.cell(row=r, column=1, value='Принятое R, кПа'); wp.cell(row=r, column=2, value='=R_GR')
r += 1
wp.cell(row=r, column=1, value='Не влияют на фундамент в П³: пучинистость, сейсмика, рельеф, ветер, город. Глубина промерзания меняет только высоту подколонника.').font = f_note

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
    ('Буронабивные сваи (если П³ требует)', '=BORED_N', 'шт', '=P_BORED'),
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

# ---------------------------------------------------------------- Таблицы П³
grid = json.load(open(os.path.join(HERE, 'p3_grid_240.json')))
G = {(g['B'], g['H'], g['snow']): g for g in grid}
BS, HS, SS = [12, 18, 24, 30, 36], [4, 6, 8, 10, 12, 14], [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]
wt = wb.create_sheet('Таблицы П³')
title(wt, 'Металлоёмкость и подбор в П³: пролёт × высота × снег (240 расчётов в самом П³)',
      'Здание 30 м, шаг рам 6 м, двускатная 6°, С255, PIR 120/100, полные связи. Цифры — прямо из П³, 18.11.2026.', 9)
for col, w in zip('ABCDEFGHI', (26, 12, 12, 12, 12, 12, 12, 12, 12)):
    wt.column_dimensions[col].width = w
r = 4
fill_bad = PatternFill('solid', fgColor='F8CBAD')
section(wt, r, 'Коэффициент использования k (от высоты не зависит). Красное — профиль не проходит (k > 1), но П³ всё равно считает металл', 9); r += 1
wt.cell(row=r, column=1, value='Снег, кПа \\ пролёт, м').font = f_bold
for j, B_ in enumerate(BS, 2):
    wt.cell(row=r, column=j, value=B_).font = f_bold
r += 1
for sn in SS:
    wt.cell(row=r, column=1, value=sn)
    for j, B_ in enumerate(BS, 2):
        g = G[(B_, 6, sn)]
        c = wt.cell(row=r, column=j, value=g['k']); c.number_format = '0.00'
        if g['k'] > 1:
            c.fill = fill_bad
    r += 1
wt.cell(row=r, column=1, value='k = 9,00 — предел П³: балка перегружена в 9 и более раз. Москва и СПб (III район) = 1,5 кПа.').font = f_note
r += 2
section(wt, r, 'Стропильная балка / шаг прогонов, м / прогон', 9); r += 1
wt.cell(row=r, column=1, value='Снег, кПа \\ пролёт, м').font = f_bold
for j, B_ in enumerate(BS, 2):
    wt.cell(row=r, column=j, value=B_).font = f_bold
r += 1
for sn in SS:
    wt.cell(row=r, column=1, value=sn)
    for j, B_ in enumerate(BS, 2):
        g = G[(B_, 6, sn)]
        wt.cell(row=r, column=j, value=f"{g['raf']} / {g['ps']:.1f} / {g['pur']}")
    r += 1
wt.cell(row=r, column=1, value='Колонна во всех 240 вариантах — 40К1 (П³ проверяет её только на сжатие).').font = f_note
r += 2
for sn in SS:
    section(wt, r, f'Металлоёмкость, кг/м² — снег {sn:.1f} кПа', 9); r += 1
    wt.cell(row=r, column=1, value='Высота, м \\ пролёт, м').font = f_bold
    for j, B_ in enumerate(BS, 2):
        wt.cell(row=r, column=j, value=B_).font = f_bold
    r += 1
    for H_ in HS:
        wt.cell(row=r, column=1, value=H_)
        for j, B_ in enumerate(BS, 2):
            g = G[(B_, H_, sn)]
            c = wt.cell(row=r, column=j, value=round(g['p3'] * 1000 / (30 * B_), 1)); c.number_format = '0.0'
            if g['k'] > 1:
                c.fill = fill_bad
        r += 1
    r += 1
section(wt, r, 'Фундаменты П³ (без геологии, R = 180 кПа), H = 6 м', 9); r += 1
wt.cell(row=r, column=1, value='Снег, кПа \\ пролёт, м').font = f_bold
for j, B_ in enumerate(BS, 2):
    wt.cell(row=r, column=j, value=B_).font = f_bold
r += 1
for sn in SS:
    wt.cell(row=r, column=1, value=sn)
    for j, B_ in enumerate(BS, 2):
        wt.cell(row=r, column=j, value=G[(B_, 6, sn)]['found'].replace(' м ×', '×').replace('Ф-', 'Ф')).font = Font(name=F, size=8)
    r += 1
wt.cell(row=r, column=1, value='Ф1 — 4 угловые колонны, Ф2 — остальные. Размер: сторона × сторона × толщина плиты, м.').font = f_note

# ---------------------------------------------------------------- Сверка с П³
wv = wb.create_sheet('Сверка с П³')
title(wv, 'Сверка формул калькулятора с П³: 240 вариантов', 'Столбец «Модель» — те же формулы, что на листах «Расчёт» и «Подбор П³».', 11)
hdr = ('L', 'B', 'H', 'Снег', 'МК П³, т', 'МК модель, т', 'Ошибка', 'k П³', 'Стропило', 'Прогон', 'Фундаменты П³')
for i, h in enumerate(hdr, 1):
    c = wv.cell(row=4, column=i, value=h); c.font = Font(name=F, size=10, bold=True, color='FFFFFF'); c.fill = fill_h1
    wv.column_dimensions[get_column_letter(i)].width = 11
wv.column_dimensions['K'].width = 50
r = 5
for g in grid:
    for i, k in enumerate(('L', 'B', 'H', 'snow', 'p3', 'model'), 1):
        wv.cell(row=r, column=i, value=g[k]).font = f_norm
    wv.cell(row=r, column=7, value=f'=IF(E{r}=0,0,F{r}/E{r}-1)').number_format = '0.00%'
    for i, k in ((8, 'k'), (9, 'raf'), (10, 'pur'), (11, 'found')):
        wv.cell(row=r, column=i, value=g[k]).font = f_norm
    r += 1
wv.cell(row=r + 1, column=1, value='Средняя абсолютная ошибка').font = f_bold
wv.cell(row=r + 1, column=7, value=f'=SUMPRODUCT(ABS(G5:G{r-1}))/COUNT(G5:G{r-1})').number_format = '0.00%'
wv.cell(row=r + 2, column=1, value='Профили, коэффициенты использования и размеры фундаментов совпали во всех 240 вариантах.').font = f_note

# ---------------------------------------------------------------- Методика
wm = wb.create_sheet('Как считает П³')
title(wm, 'Как считает конструктор П³ — простыми словами', None, 1)
wm.column_dimensions['A'].width = 140
text = [
    'Откуда данные',
    '• 18.11.2026 разобран код конструктора p3-platform.ru/constructor и прогнано 313 вариантов в самом П³ (пролёты 12–36 м, высоты 4–14 м, снег 0,5–4 кПа, все грунты, вода, промерзание, сейсмика, ветер, краны, многопролётные, сталь, панели).',
    '• Формулы этого файла дают те же профили, коэффициенты и фундаменты, что П³, во всех 240 вариантах сетки; масса металла — в пределах 0,03 %.',
    '',
    '1. Снег',
    '• В П³ есть выбор «снеговой район», но расчёт его не использует. Считается только число в поле «Снеговая нагрузка, кПа». По умолчанию там 1,8 при районе III (у III района по СП 1,5).',
    '• Нагрузка на кровлю = (снег + 0,32) × γf (γf = 1,2). Снег в расчёте не меньше 0,5 кПа.',
    '• Снег влияет на: шаг прогонов, профиль стропила, прогона и карнизной балки, размер фундаментов. Колонну не меняет.',
    '',
    '2. Металл и профили',
    '• Стропило П³ считает как простую балку на весь пролёт (без жёсткой рамы): изгиб и прогиб L/220. Выбирает первый из 40Б1 → 45Б1 → 50Б1 → 55Б1 с k ≤ 0,88.',
    '• Если ни один не проходит, ставит 55Б1 и пишет k (до 9). Пролёт 18 м проходит только при снеге 0,5 кПа; 24–36 м не проходят никогда. Металлоёмкость П³ для таких зданий занижена: реальная рама будет тяжелее.',
    '• Колонна: только сжатие с устойчивостью (N = шаг × весь пролёт × нагрузка × 1,08), ветер и изгиб от рамы не считаются. Поэтому почти всегда 40К1.',
    '• Масса 40К1 в П³ — 72,6 кг/м, а по его же размерам сечения — 131,6 кг/м. Масса колонн занижена на 45 %. В калькуляторе это переключатель «Масса колонн».',
    '• Прогоны Z250/Z300: пролёт = шаг рам. Шаг прогонов = допустимый пролёт панели × √(1,8 / (снег + 0,25)), от 0,9 до 2,8 м. Ряды раскладываются по горизонтали + ряд у карниза + ряд у конька.',
    '• Связи 20Б1: по стенам в крайних панелях и через 3 панели после 30 м; по кровле — крест в каждой второй панели на каждом скате.',
    '• Длина колонны = высота + половина высоты стропила + 0,03 м. Стропило = скат − 0,24 м.',
    '',
    '3. Что НЕ влияет на расчёт в П³ (проверено и в коде, и прогоном)',
    '• Снеговой и ветровой район (выпадающие списки), ветровая нагрузка, сейсмичность (7, 8, 9 баллов), пучинистость, рельеф, город.',
    '• Тип грунта и даже введённое R, если выбрано «Нет геологии» или тип «Не знаю»: R всегда 180 кПа. Исключения: торф (сваи, плита +60 мм) и насыпной/рыхлый (плита +30 мм).',
    '',
    '4. Фундаменты',
    '• Реакция колонны = (грузовая площадь × (снег + 0,35) + доля веса металла и стен) × 1,2.',
    '• Площадь подошвы = 1,25 × N / R. Сторона от 1,1 до 4 м с шагом 0,1; толщина = 0,38 + 0,09 × сторона (0,45–0,9 м); подколонник 0,55–1,0 м, высота = промерзание − толщина + 0,15 (0,45–1,1 м).',
    '• Сваи, если: торф, R < 95 кПа, насыпной грунт с водой < 1 м, площадь > 9 м² или N > 1700 кН при R < 180. Куст 4/6/9 свай Ø300/400 длиной 6 м (или до несущего слоя).',
    '• R по таблице: скальный 800, крупнообломочный 500, песок крупный 420, средний 300, мелкий 210, пылеватый 150, супесь 180, суглинок 200, глина 240, насыпной 120, торф 60. Плотный ×1,15, рыхлый ×0,72, вода < 1 м ×0,78, 1–3 м ×0,9.',
    '• Анкеры 4/8/12 шт на колонну (N < 700 / < 1500 / больше), Ø24/30/36. Арматура 95 кг/м³ (на сваях 125).',
    '',
    '5. Плита пола',
    '• Нагрузка т/м² × 10 = кПа; расчётная = (нагрузка + вес плиты) × γf. Толщина 120/150/180/220/260/300/350 мм при расчётной > 0/8/15/30/50/75/105 кПа.',
    '',
    '6. Что заметно в П³ (стоит учитывать при сравнении с нашими КП)',
    '• Рама не рассчитывается как рама; при больших пролётах П³ не может подобрать профиль, но металл всё равно показывает.',
    '• Масса колонн занижена на 45 %. Фронтоны в площади стен учтены дважды.',
    '• Нет ферм, винтовых свай, пола из плит ПАГ, вертикальной раскладки панелей с ригелями, фахверка при раскладке «как пролёты».',
    '',
    'Как устроен этот файл',
    '• «Ввод» — параметры. «Расчёт» — объёмы. «Подбор П³» — проверка профилей и фундаментов по алгоритму П³. «Смета» — стоимость. «Справочник» — таблицы и цены. «Таблицы П³» — металлоёмкость из самого П³. «Сверка с П³» — 240 проверок.',
    '• Режим «КП (фермы)» повторяет КП «Ангар 18 × 30 × 6» (рамы с фермами, ригели, фахверк, швеллер, винтовые сваи, пол ПАГ).',
    '• Это предварительный расчёт для КП. Окончательные сечения — по расчёту КМ и ИГИ.',
]
for i, t in enumerate(text, 3):
    c = wm.cell(row=i, column=1, value=t)
    c.font = f_bold if t and not t.startswith('•') else f_norm
    c.alignment = Alignment(wrap_text=True, vertical='top')

order = ['Ввод', 'Расчёт', 'Подбор П³', 'Смета', 'Справочник', 'Таблицы П³', 'Сверка с П³', 'Как считает П³']
wb._sheets = [wb[n] for n in order]
wb.save(OUT)
print('saved', OUT)
