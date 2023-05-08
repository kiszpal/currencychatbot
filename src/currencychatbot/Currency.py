import response
from forex_python.converter import CurrencyRates
import pandas
from datetime import datetime, timedelta
from matplotlib import pyplot as plt
import io
import discord


class Currency:
    def __init__(self):
        self._currencies = CurrencyRates()

    @property
    def rates(self):
        return self._currencies

    def get_curr_rates(self, base, desired_currencies):
        rates = self.rates.get_rates(base)
        match len(desired_currencies):
            case 1:
                return f"{base} is worth {self.rates.get_rate(base, desired_currencies[0].upper())} {desired_currencies[0].upper()}"
            case 0:
                return response.BaseResponse().response

        values = list()
        try:
            for currency in desired_currencies:
                values.append(rates[currency.upper()])
        except IndexError:
            return "The inputs are in wrong format."

        df = pandas.DataFrame({"Currencies": desired_currencies, "": values}).set_index("Currencies")
        return df

    def change(self, what, desired, amount=1):
        if len(desired) != 1:
            return "Wromg usage!"
        desired = desired[0]
        return str(round(int(amount) * self.rates.get_rate(what.upper(), desired.upper()), 2))

    def historical_rates(self, currencies, desired, days=1, plot=False):
        '''
        During tests, it turned out forex_python sometimes is giving false data.

        :param currencies: A list of strings each representing a currency.
        :param desired: A string that represents a currency wich we want to change to
        :param days: Number of days we want to yield data of.
        :param plot: Boolean value to decide if the data should be shown ona  plot.
        :return:
        '''

        if len(desired) != 1:
            return "Currency declarations are always 3 characters long!"
        desired = desired[0].upper()

        historical_rates = dict()
        dates = set()
        match len(currencies):
            case 1:
                plot = False
            case 0:
                return response.BaseResponse().response

        for currency in currencies:
            currency = currency.upper()
            if currency not in historical_rates.keys():
                historical_rates[currency] = dict()

            for i in range(int(days), -1, -1):
                date = (datetime.now() - timedelta(days=i)).date()
                historical_rates[currency][date] = round(self.rates.get_rates(currency, date)[desired], 2)
                dates.add(date)

        if plot:
            x_axis = [f"{(datetime.now() - timedelta(days=i)).date().month}-{(datetime.now() - timedelta(days=i)).date().day}" for i in range(int(days) + 1)]
            y_axis = list()
            for currency in historical_rates.keys():
                y_axis.append({currency: [historical_rates[currency][date] for date in historical_rates[currency]]})
            for y_dict in y_axis:
                for y_label, y_data in y_dict.items():
                    plt.plot(x_axis, y_data, label=y_label)

            plt.ylabel(desired)
            plt.title('Rates')
            plt.legend()
            data_stream = io.BytesIO()
            plt.savefig(data_stream, format="png", bbox_inches="tight", dpi=300)
            data_stream.seek(0)
            chart = discord.File(data_stream, filename="plotted_data.png")
            return chart
        else:
            df = pandas.DataFrame(historical_rates)
            return df
