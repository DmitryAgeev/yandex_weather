import asyncio
import csv
import sys
import traceback
import os
from datetime import datetime
from sql import SQLighter
from yaweather import Russia, YaWeatherAsync


def csv_pack(name, params, mode='a+'):
    with open(name + '.csv', mode, newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_ALL, delimiter=',')
        for i in range(len(params)):
            params[i] = str(params[i])
        writer.writerow(params)


def save(date, pressure, temp, field, city):
    if len(pressure) < 3:
        return

    print('save')

    date = date.strftime("%d.%m.%Y")
    maximum = max(pressure)
    minimum = min(pressure)

    if field != '-':
        print(field)
        if int(field):
            field = 'неустойчивое'
        else:
            field = 'спокойное'

    if len(temp) < 4:
        temp += ['']
    diff = maximum - minimum
    index_diff = pressure.index(maximum) - pressure.index(minimum)

    atmosphere = '-'

    if diff >= 5:
        if index_diff > 0:
            atmosphere = 'ожидается резкое увеличение атмосферного давления'
        else:
            atmosphere = 'ожидается резкое падение атмосферного давления'

    mean_temp = round(sum(temp[:3]) / 3)

    csv_pack(city, [date] + temp + [mean_temp, field, atmosphere])


async def main(city_param, city):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "weather_db.db")

    db = SQLighter(db_path)

    try:
        csv_pack(city,
                 ['Дата', 'Утро', 'День', 'Вечер', 'Ночь', 'Средняя температура за световой день', 'Магнитное поле',
                  'Атмосферное давление'], mode='w')
        async with YaWeatherAsync(api_key='83027ebf-8b07-4778-8b47-062d044910d3') as y:
            result = await y.forecast(city_param, limit=10)
            pressure = []
            temp = []
            date = result.forecasts[0].date

            try:
                field = result.forecasts[0].biomet['condition'][-1]
            except:
                field = '-'

            for i in range(len(result.forecasts)):
                forecast = result.forecasts[i]
                for part in forecast.parts:
                    when, weather = part
                    if 'short' in when:
                        continue
                    # print(weather)
                    print(f'{forecast.date} {when}| {weather.daytime} °C, {weather.condition}')
                    pressure.append(weather.pressure_mm)
                    temp.append(weather.temp_avg)

                    print(i == len(result.forecasts) - 1)
                    if when == 'night' or (i == len(result.forecasts) - 1 and when == 'evening'):
                        save(date, pressure, temp, field, city)
                        date = forecast.date
                        pressure = []
                        temp = []
                        try:
                            field = forecast.biomet['condition'][-1]
                        except:
                            field = '-'
                    else:
                        date = forecast.date

        db.save_sql('Успех', datetime.now(), city)
    except:
        traceback.print_exc()
        db.save_sql('Провал', datetime.now(), city)


if __name__ == '__main__':
    param = sys.argv[1]
    param = param.split('-')
    exec("%s = %s.%s" % ('city_param', param[0], param[1]))
    print(city_param)

    asyncio.run(main(city_param, param[1]))
