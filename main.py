from tkinter import *
import tkinter.ttk as ttk
import datetime
from datetime import date
import urllib.request
import xml.dom.minidom
import matplotlib
import matplotlib.pyplot as plt


def get_date(days_delta=0, edit_format=True, day_start_from=date.today()):
    day = day_start_from
    if edit_format:
        return format_date(day - datetime.timedelta(days=days_delta))
    return day - datetime.timedelta(days=days_delta)


def format_date(day=date.today()):
    return day.strftime("%d/%m/%Y")


def month_name(month=1):
    if month == 1:
        return "Январь"
    if month == 2:
        return "Февраль"
    if month == 3:
        return "Март"
    if month == 4:
        return "Апрель"
    if month == 5:
        return "Май"
    if month == 6:
        return "Июнь"
    if month == 7:
        return "Июль"
    if month == 8:
        return "Август"
    if month == 9:
        return "Сентябрь"
    if month == 10:
        return "Октябрь"
    if month == 11:
        return "Ноябрь"
    return "Декабрь"


def month_short_name(month=1):
    if month == 1:
        return "янв"
    if month == 2:
        return "фев"
    if month == 3:
        return "мар"
    if month == 4:
        return "апр"
    if month == 5:
        return "май"
    if month == 6:
        return "июн"
    if month == 7:
        return "июл"
    if month == 8:
        return "авг"
    if month == 9:
        return "сен"
    if month == 10:
        return "окт"
    if month == 11:
        return "ноя"
    return "дек"


def get_quarter(day=date.today()):
    day = day.replace(day=1)
    month = day.month
    if month in [3, 6, 9, 12]:
        return day
    if month in [1, 4, 7, 10]:
        return prev_month(day)
    if month in [2, 5, 8, 11]:
        return prev_month(prev_month(day))


def quarter_name(month=12):
    if month == 3:
        return "Весна"
    if month == 6:
        return "Лето"
    if month == 9:
        return "Осень"
    return "Зима"  # day = 12


def prev_month(day=date.today()):
    month = day.month - 1
    if month == 0:
        day = day.replace(year=day.year-1, month=12)
        return day
    else:
        day = day.replace(month=day.month-1)
        return day


def request(days_delta=0):
    response = urllib.request.urlopen(f"http://www.cbr.ru/scripts/XML_daily.asp?date_req={get_date(days_delta)}")
    return response


def get_valutes(days_delta=0, with_rub=False):
    exit_dict = dict()
    response = request(days_delta)
    dom = xml.dom.minidom.parse(response)
    dom.normalize()
    nodeArray = dom.getElementsByTagName("Valute")
    for node in nodeArray:
        childList = node.childNodes
        for child in childList:
            if child.nodeName not in exit_dict:
                exit_dict[child.nodeName] = []
            exit_dict[child.nodeName].append(child.childNodes[0].nodeValue)
    if with_rub:
        exit_dict["NumCode"].insert(0, "001")
        exit_dict["CharCode"].insert(0, "RUB")
        exit_dict["Nominal"].insert(0, "1")
        exit_dict["Name"].insert(0, "Российский рубль")
        exit_dict["Value"].insert(0, "1")
    return exit_dict


if __name__ == '__main__':
    print(get_valutes(with_rub=True))
    window = Tk()
    window.title("Валютная приложуха")
    window.geometry("512x288")

    today_dict = get_valutes(with_rub=True)
    today = date.today()
    tab_control = ttk.Notebook(window)

    #
    ##
    # Вкладка 1 - Конвертер валют
    tab_converter = ttk.Frame(tab_control)
    tab_control.add(tab_converter, text="Конвертер валют")

    comb_valutes_1 = ttk.Combobox(tab_converter)
    comb_valutes_1["state"] = "readonly"
    comb_valutes_1["values"] = today_dict["Name"]
    comb_valutes_1.current(0)
    comb_valutes_1.grid(column=0, row=0)

    comb_valutes_2 = ttk.Combobox(tab_converter)
    comb_valutes_2["state"] = "readonly"
    comb_valutes_2["values"] = today_dict["Name"]
    comb_valutes_2.current(0)
    comb_valutes_2.grid(column=0, row=2)

    edit_text = Entry(tab_converter)
    edit_text["justify"] = "center"
    edit_text.insert(0, "1")
    edit_text.grid(column=1, row=0)
    text_view = Label(tab_converter, text="1")
    text_view.grid(column=1, row=2)

    def on_click_convert():
        amount = float(edit_text.get().replace(',', '.'))
        value_1 = float(today_dict["Value"][comb_valutes_1.current()].replace(',', '.'))
        nominal_1 = float(today_dict["Nominal"][comb_valutes_1.current()].replace(',', '.'))
        value_2 = float(today_dict["Value"][comb_valutes_2.current()].replace(',', '.'))
        nominal_2 = float(today_dict["Nominal"][comb_valutes_2.current()].replace(',', '.'))

        result = (amount * value_1 / nominal_1) / (value_2 / nominal_2)
        text_view.config(text=result)

    btn_convert = Button(tab_converter, text="Конвертировать", command=on_click_convert)
    btn_convert.grid(column=2, row=1)

    # Конец вкладки 1
    ##
    #

    #
    ##
    # Вкладка 2 - Динамика курса
    tab_dynamics = ttk.Frame(tab_control)
    tab_control.add(tab_dynamics, text="Динамика курса")

    label_1 = Label(tab_dynamics, text="Валюта")
    label_1.grid(column=0, row=0)
    label_2 = Label(tab_dynamics, text="Период")
    label_2.grid(column=1, row=0)

    comb_valutes = ttk.Combobox(tab_dynamics)
    comb_valutes["state"] = "readonly"
    comb_valutes["values"] = today_dict["Name"][1:]
    comb_valutes.current(0)
    comb_valutes.grid(column=0, row=1)



    # 1 - week  2 - month  3 - quarter  4 - year
    period = IntVar()
    dates_list = []

    def change_periods():
        per = period.get()
        if per == 1:
            periods_list = [get_date(6)+"-"+get_date(), get_date(13)+"-"+get_date(7),
                            get_date(20)+"-"+get_date(14), get_date(27)+"-"+get_date(21)]
            dates_list.clear()
            dates_list.append({"start": get_date(6, False), "end": get_date(edit_format=False)})
            dates_list.append({"start": get_date(13, False), "end": get_date(7, False)})
            dates_list.append({"start": get_date(20, False), "end": get_date(14, False)})
            dates_list.append({"start": get_date(27, False), "end": get_date(21, False)})
            comb_periods.config(values=periods_list)
        elif per == 2:
            month_this = today.replace(day=1)
            month_prev = prev_month(month_this)
            month_prev_2 = prev_month(month_prev)
            month_prev_3 = prev_month(month_prev_2)
            periods_list = [month_name(month_this.month)+" "+str(month_this.year),
                            month_name(month_prev.month)+" "+str(month_prev.year),
                            month_name(month_prev_2.month)+" "+str(month_prev_2.year),
                            month_name(month_prev_3.month)+" "+str(month_prev_3.year)]
            dates_list.clear()
            dates_list.append({"start": month_this, "end": today})
            dates_list.append({"start": month_prev, "end": get_date(1, False, month_this)})
            dates_list.append({"start": month_prev_2, "end": get_date(1, False, month_prev)})
            dates_list.append({"start": month_prev_3, "end": get_date(1, False, month_prev_2)})
            comb_periods.config(values=periods_list)
        elif per == 3:
            quart_this = get_quarter(today)
            quart_prev = get_quarter(get_date(1, False, quart_this))
            quart_prev_2 = get_quarter(get_date(1, False, quart_prev))
            quart_prev_3 = get_quarter(get_date(1, False, quart_prev_2))
            period_list = [quarter_name(quart_this.month)+" "+str(quart_this.year),
                           quarter_name(quart_prev.month)+" "+str(quart_prev.year),
                           quarter_name(quart_prev_2.month)+" "+str(quart_prev_2.year),
                           quarter_name(quart_prev_3.month)+" "+str(quart_prev_3.year)]
            dates_list.clear()
            dates_list.append({"start": quart_this, "end": today})
            dates_list.append({"start": quart_prev, "end": get_date(1, False, quart_this)})
            dates_list.append({"start": quart_prev_2, "end": get_date(1, False, quart_prev)})
            dates_list.append({"start": quart_prev_3, "end": get_date(1, False, quart_prev_2)})
            comb_periods.config(values=period_list)
        elif per == 4:
            year_this = today.replace(month=1, day=1)
            year_prev = year_this.replace(year=year_this.year-1)
            year_prev_2 = year_prev.replace(year=year_prev.year-1)
            year_prev_3 = year_prev_2.replace(year=year_prev_2.year-1)
            period_list = [str(year_this.year), str(year_prev.year), str(year_prev_2.year), str(year_prev_3.year)]

            dates_list.clear()
            dates_list.append({"start": year_this, "end": today})
            dates_list.append({"start": year_prev, "end": year_prev.replace(month=12, day=31)})
            dates_list.append({"start": year_prev_2, "end": year_prev_2.replace(month=12, day=31)})
            dates_list.append({"start": year_prev_3, "end": year_prev_3.replace(month=12, day=31)})
            comb_periods.config(values=period_list)
        comb_periods.current(0)

    week_btn = Radiobutton(tab_dynamics, text="Неделя", value=1, variable=period, command=change_periods)
    week_btn.select()
    week_btn.grid(column=1, row=1, sticky=W)
    month_btn = Radiobutton(tab_dynamics, text="Месяц", value=2, variable=period, command=change_periods)
    month_btn.grid(column=1, row=2, sticky=W)
    quarter_btn = Radiobutton(tab_dynamics, text="Квартал", value=3, variable=period, command=change_periods)
    quarter_btn.grid(column=1, row=3, sticky=W)
    year_btn = Radiobutton(tab_dynamics, text="Год", value=4, variable=period, command=change_periods)
    year_btn.grid(column=1, row=4, sticky=W)

    label_3 = Label(tab_dynamics, text="Выбор периода")
    label_3.grid(column=2, row=0)

    comb_periods = ttk.Combobox(tab_dynamics)
    comb_periods["state"] = "readonly"
    change_periods()
    comb_periods.grid(column=2, row=1)

    def build_graf():
        start = dates_list[comb_periods.current()]["start"]
        end = dates_list[comb_periods.current()]["end"]
        per = period.get()
        window.geometry("1280x800")
        matplotlib.use('TkAgg')
        fig = plt.figure()
        canvas = matplotlib.backends.backend_tkagg.FigureCanvasTkAgg(fig, master=tab_dynamics)
        plot_widget = canvas.get_tk_widget()
        fig.clear()
        x_y = {"x": [], "y": []}
        day = start
        if per == 1:
            while day <= end:
                day_dict = get_valutes((today-day).days)
                course = float((day_dict["Value"][comb_valutes.current()]).replace(',', '.')) / float((day_dict["Nominal"][comb_valutes.current()]).replace(',', '.'))
                x_y["y"].append(course)
                x_y["x"].append(get_date((today-day).days, False).strftime("%d/%m"))
                day = get_date(-1, False, day)
            plt.plot(x_y["x"], x_y["y"])
            xtick_location = x_y["x"]
            xtick_labels = [x[::] for x in x_y["x"]]
            plt.xticks(ticks=xtick_location, labels=xtick_labels, fontsize=10, alpha=.7)
        elif per == 2:
            while day <= end:
                day_dict = get_valutes((today-day).days)
                course = float((day_dict["Value"][comb_valutes.current()]).replace(',', '.')) / float((day_dict["Nominal"][comb_valutes.current()]).replace(',', '.'))
                x_y["y"].append(course)
                x_y["x"].append(get_date((today-day).days, False).strftime("%d/%m"))
                day = get_date(-1, False, day)
            plt.plot(x_y["x"], x_y["y"])
            xtick_location = x_y["x"][::2]
            xtick_labels = [x[::] for x in x_y["x"][::2]]
            plt.xticks(ticks=xtick_location, labels=xtick_labels, fontsize=6, alpha=.7)
        elif per == 3:
            while day <= end:
                day_dict = get_valutes((today-day).days)
                course = float((day_dict["Value"][comb_valutes.current()]).replace(',', '.')) / float((day_dict["Nominal"][comb_valutes.current()]).replace(',', '.'))
                x_y["y"].append(course)
                x_y["x"].append(get_date((today-day).days, False).strftime("%d/%m"))
                day = get_date(-3, False, day)
            plt.plot(x_y["x"], x_y["y"])
            xtick_location = x_y["x"][::2]
            xtick_labels = [x[::] for x in x_y["x"][::2]]
            plt.xticks(ticks=xtick_location, labels=xtick_labels, fontsize=6, alpha=.7)
        elif per == 4:
            while day <= end:
                day_dict = get_valutes((today-day).days)
                course = float((day_dict["Value"][comb_valutes.current()]).replace(',', '.')) / float((day_dict["Nominal"][comb_valutes.current()]).replace(',', '.'))
                x_y["y"].append(course)
                x_y["x"].append(get_date((today-day).days, False))
                day = get_date(-8, False, day)

            plt.plot(x_y["x"], x_y["y"])
            xtick_location = x_y["x"][::4]
            for i in range(len(x_y["x"])):
                buf_date = x_y["x"][i]
                x_y["x"][i] = month_short_name(buf_date.month)

            xtick_labels = [x[::] for x in x_y["x"][::4]]
            plt.xticks(ticks=xtick_location, labels=xtick_labels, fontsize=6, alpha=.7)
        plt.grid()
        plot_widget.grid(column=2, row=5)


    build_graf_btn = Button(tab_dynamics, text="Построить график", command=build_graf)
    build_graf_btn.grid(column=0, row=5)
    # Конец вкладки 2
    ##
    #

    tab_control.pack(expand=1, fill="both")

    window.mainloop()
