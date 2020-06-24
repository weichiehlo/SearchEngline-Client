
import backend_database

import numpy as np

import matplotlib.pyplot as plt

from matplotlib.figure import Figure
import statistics
import matplotlib as mpl
from scipy.stats import gaussian_kde
import matplotlib.patches as mpatches
from scipy.optimize import curve_fit


class graphFigure(Figure):

    def __init__(self, *args, figtitle='DEFAULT TITLE', **kwargs):
        """
        custom kwarg figtitle is a figure title
        
        """
        super().__init__(*args, **kwargs)
        #self.text(0.5, 0.95, figtitle, ha='center')

    def find_avg_pos(self,avg,labels):
        for idx, x_tick in enumerate(labels):
            if float(x_tick) > avg:
                total_dif = float(x_tick) - float(labels[idx - 1])
                dif = avg - float(labels[idx - 1])
                try:
                    return idx - 1 + dif / total_dif
                except ZeroDivisionError:
                    return 0
        return len(labels)


    def plotbar_sensor(self,table_list):
        model_list = [x[:6] for x in table_list]

        self.ax = ""

        self.labels,self.sensor_data,self.interval = backend_database.MyDatabase.return_sensor_graph_data_dif_model(table_list)


        self.y_range_count = {}
        self.total = {}
        self.y_range_percent = {}
        self.bar_list = []
        self.average =[]

        for idx, val in enumerate(table_list):
            temp_dbms = backend_database.MyDatabase(backend_database.POSTGRES, dbname=model_list[idx])
            if idx == 0:
                self.y_range_count[val] = self.sensor_data["first_sensor"]
                unit = temp_dbms.return_unit_from_graph(table_list[idx])
            elif idx == 1:
                self.y_range_count[val] = self.sensor_data["second_sensor"]
            elif idx == 2:
                self.y_range_count[val] = self.sensor_data["third_sensor"]
            else:
                print("error graphing sensor not 123")


            self.total[val] = (temp_dbms.return_total_count(table_list[idx]))
            self.bar_list.append(val)
            self.average.append(temp_dbms.return_sensor_avg(table_list[idx][:-6]))


        for idx,val in enumerate(table_list):



            self.y_range_percent[val] = [ float(format(count / self.total[val] * 100, '.2f')) if count != 0 else count for count in self.y_range_count[val]]

        x = np.arange(len(self.labels))  # the label locations
        width = 0.30  # the width of the bars
        self.num_rec = len(table_list)

        self.ax = self.subplots()



        if self.num_rec == 1:
            self.rects1 = self.ax.bar(x, self.y_range_percent[self.bar_list[0]], width, label=self.bar_list[0])
            self.autolabel_percent(self.rects1,self.num_rec)

            max_height = max(self.y_range_percent[self.bar_list[0]])+1

            avg = self.find_avg_pos(float(self.average[0]),self.labels)
            plt.vlines([avg], 0, max_height, colors=['#3658D8'])


            plt.annotate('Average: '+self.average[0]+" "+unit, xy=(avg,max_height/2), xytext=(avg+0.5,max_height+1),arrowprops=dict(facecolor='#3658D8', shrink=0.05))

        elif self.num_rec == 2:
            self.rects1 = self.ax.bar(x - width/2, self.y_range_percent[self.bar_list[0]], width, label=self.bar_list[0])
            self.rects2 = self.ax.bar(x + width/2, self.y_range_percent[self.bar_list[1]], width, label=self.bar_list[1])
            self.autolabel_percent(self.rects1,self.num_rec)
            self.autolabel_percent(self.rects2,self.num_rec)

            max_height_1 = max(self.y_range_percent[self.bar_list[0]]) + 1
            max_height_2 = max(self.y_range_percent[self.bar_list[1]]) + 1
            avg_1 = self.find_avg_pos(float(self.average[0]),self.labels)
            avg_2 = self.find_avg_pos(float(self.average[1]),self.labels)

            plt.vlines([avg_1,avg_2], 0, max([max_height_1,max_height_2])+5, colors=['#3658D8', '#F59147'])


            plt.annotate('Average: '+self.average[0]+" "+unit, xy=(avg_1, max_height_1/2), xytext=(avg_1 + 0.5, max_height_1/2+1),
                         arrowprops=dict(facecolor='#3658D8', shrink=0.05))
            plt.annotate('Average: '+self.average[1]+" "+unit, xy=(avg_2, max_height_2/2), xytext=(avg_2 + 0.5, max_height_2/2+1),
                         arrowprops=dict(facecolor='#F59147', shrink=0.05))

            plt.annotate('Difference: ' + str(abs(round(float(self.average[1]) - float(self.average[0]),2)))+" "+unit,
                         xy=(max([avg_1,avg_2]), max([max_height_1,max_height_2])+3), xytext=(max([avg_1,avg_2])+0.1,max([max_height_1,max_height_2])+4))

            plt.annotate(s='', xy=(avg_1, max([max_height_1,max_height_2])+3), xytext=(avg_2,max([max_height_1,max_height_2])+3), arrowprops=dict(arrowstyle='<->'))


        elif self.num_rec == 3:
            self.rects1 = self.ax.bar(x - width, self.y_range_percent[self.bar_list[0]], width, label=self.bar_list[0])
            self.rects2 = self.ax.bar(x, self.y_range_percent[self.bar_list[1]], width, label=self.bar_list[1])
            self.rects3 = self.ax.bar(x + width, self.y_range_percent[self.bar_list[2]], width, label=self.bar_list[2])
            self.autolabel_percent(self.rects1,self.num_rec)
            self.autolabel_percent(self.rects2,self.num_rec)
            self.autolabel_percent(self.rects3,self.num_rec)

            max_height_1 = max(self.y_range_percent[self.bar_list[0]]) + 1
            max_height_2 = max(self.y_range_percent[self.bar_list[1]]) + 1
            max_height_3 = max(self.y_range_percent[self.bar_list[2]]) + 1

            avg_1 = self.find_avg_pos(float(self.average[0]), self.labels)
            avg_2 = self.find_avg_pos(float(self.average[1]), self.labels)
            avg_3 = self.find_avg_pos(float(self.average[2]), self.labels)
            plt.vlines([avg_1, avg_2, avg_3], 0, max([max_height_1,max_height_2,max_height_3])+5, colors=['#3658D8', '#F59147', '#58CA3F'])
            plt.annotate('Average: '+self.average[0]+" "+unit, xy=(avg_1, max_height_1/2), xytext=(avg_1 + 0.5, max_height_1/2+1),
                         arrowprops=dict(facecolor='#3658D8', shrink=0.05))
            plt.annotate('Average: '+self.average[1]+" "+unit, xy=(avg_2, max_height_2/2), xytext=(avg_2 + 0.5, max_height_2/2+1),
                         arrowprops=dict(facecolor='#F59147', shrink=0.05))
            plt.annotate('Average: '+self.average[2]+" "+unit, xy=(avg_3, max_height_3/2), xytext=(avg_3 + 0.5, max_height_3/2+1),
                         arrowprops=dict(facecolor='#58CA3F', shrink=0.05))



            plt.annotate('Difference: ' + str(abs(round(float(self.average[1]) - float(self.average[0]), 2)))+" "+unit,
                         xy=(max([avg_1,avg_2]), max_height_1+3), xytext=(max([avg_1,avg_2])+0.1, max_height_1+4))
            plt.annotate(s='', xy=(avg_1, max_height_1+3), xytext=(avg_2, max_height_1+3), arrowprops=dict(arrowstyle='<->'))

            plt.annotate('Difference: ' + str(abs(round(float(self.average[2]) - float(self.average[1]), 2)))+" "+unit,
                         xy=(max([avg_2,avg_3]), max_height_2+3), xytext=(max([avg_2,avg_3])+0.1, max_height_2+3))
            plt.annotate(s='', xy=(avg_2, max_height_2+3), xytext=(avg_3, max_height_2+3), arrowprops=dict(arrowstyle='<->'))

            plt.annotate(
                'Difference: ' + str(abs(round(float(self.average[2]) - float(self.average[0]), 2))) + " " + unit,
                xy=(max([avg_1, avg_3]), max_height_3+3), xytext=(max([avg_1, avg_3]) + 0.1, max_height_3+4))
            plt.annotate(s='', xy=(avg_1, max_height_3+3), xytext=(avg_3, max_height_3+3), arrowprops=dict(arrowstyle='<->'))

        # Add some text for labels, title and custom x-axis tick labels, etc.
        table1_dbms = backend_database.MyDatabase(backend_database.POSTGRES, dbname=model_list[0])
        self.ax.set_ylabel('Percent(%)')
        self.ax.set_xlabel("±" +self.interval+" "+ table1_dbms.return_unit_from_graph(self.bar_list[0]))
        self.ax.set_title('Sensor Reading Distribution Bar Graph')
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(self.labels)
        self.ax.legend(loc = 'upper left')
        self.tight_layout()
        self.ax.yaxis.grid(True)
        plt.show()



    def plotbar_err_all(self,db):
        self.dbms = backend_database.MyDatabase(backend_database.POSTGRES, dbname=db)
        self.raw_count = {}
        for val in self.dbms.return_all_blacklist():
            self.raw_count[val] =  self.dbms.return_error_count(val)

        x_err = []
        y_err = []
        for idx, val in enumerate(self.raw_count):
            if self.raw_count[val] != 0:
                x_err.append(val)
                y_err.append(self.raw_count[val])
            else:
                pass


        self.ax = ""
        self.labels = x_err


        x = np.arange(len(self.labels))  # the label locations
        width = 0.30  # the width of the bars

        self.ax = self.subplots()

        self.rects1 = self.ax.bar(x, y_err, width, label="Error Count")
        self.autolabel(self.rects1,1)


        # Add some text for labels, title and custom x-axis tick labels, etc.
        self.ax.set_ylabel('Count')
        self.ax.set_xlabel('Black List Names')
        self.ax.set_title('Error Distribution Bar Graph')
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(self.labels)
        self.ax.legend()
        self.tight_layout()
        self.ax.yaxis.grid(True)
        plt.show()

    def plot_scatter(self, table, sensor_1, sensor_2, db):
        mpl.style.use('classic')

        self.dbms = backend_database.MyDatabase(backend_database.POSTGRES, dbname=db)


        x = [round(float(data),2) for data in self.dbms.return_list_of_column_view(table, sensor_1)]
        y = [round(float(data),2) for data in self.dbms.return_list_of_column_view(table, sensor_2)]


        self.ax = self.subplots()


        xy = np.vstack([x, y])
        z = gaussian_kde(xy)(xy)


        scatter = self.ax.scatter(x, y, c=z, s=50, edgecolor='')

        # Produce a legend for the ranking (colors). Even though there are 40 different
        # rankings, we only want to show 5 of them in the legend.
        legend1 = self.ax.legend(*scatter.legend_elements(num=10,func=lambda s: s*20000),
                            loc="upper left", title="Intensity")
        self.ax.add_artist(legend1)


        plt.xticks(np.arange(min(x), max(x), round((max(x)-min(x))/10,2)))
        plt.yticks(np.arange(min(y), max(y), round((max(y)-min(y))/10,2)))

        self.ax.set_ylabel(sensor_2[:-8]+" "+self.dbms.return_unit(sensor_2[:-8]))
        self.ax.set_xlabel(sensor_1[:-8]+" "+self.dbms.return_unit(sensor_1[:-8]))
        self.ax.set_title(sensor_2[:-8]+" VS "+sensor_1[:-8])
        self.ax.grid(True)

        plt.show()


    @classmethod
    def check_graph_empty(cls, blacklist, low_bound, high_bound, model):
        dbms = backend_database.MyDatabase(backend_database.POSTGRES, dbname=model)
        if model == "All":
            query = "select distinct (COUNT(reading)) as mycount from \"{}\" WHERE in_log = 'True' GROUP BY serial_number, test_date, test_type ".format(
                blacklist)

        else:
            query = "select distinct (COUNT(reading)) as mycount from \"{}\" WHERE in_log = 'True' AND serial_number LIKE '{}%%' GROUP BY serial_number, test_date, test_type ".format(
                blacklist, model)

        avaliable_count = sorted([x[0] for x in dbms.query_return_all_data(query) if
                           (x[0] >= low_bound and x[0] <= high_bound)])
        x_err = []
        y_err = []
        if not avaliable_count:
            pass
        else:
            for x in avaliable_count:
                black_count = dbms.return_error_count_cond(blacklist,x,model)
                if black_count != 0:
                    x_err.append(x)
                    y_err.append(black_count)
                else:
                    pass

        failure_rate = sum(y_err) / dbms.return_sn_count_cond(blacklist, model) * 100

        return [x_err,y_err,failure_rate]

    @classmethod
    def check_err_low_high(cls, blacklist, model, db):
        dbms = backend_database.MyDatabase(backend_database.POSTGRES, dbname=db)
        if model == "All":
            maxquery = "SELECT MAX (mycount) from (select distinct (COUNT(reading)) as mycount from \"{}\" WHERE in_log = 'True' GROUP BY serial_number, test_date, test_type) AS \"Dummy\"".format(
                blacklist)
            minquery = "SELECT MIN (mycount) from (select distinct (COUNT(reading)) as mycount from \"{}\" WHERE in_log = 'True' GROUP BY serial_number, test_date, test_type) AS \"Dummy\"".format(
                blacklist)

        else:
            maxquery = "SELECT MAX (mycount) from (select distinct (COUNT(reading)) as mycount from \"{}\" WHERE in_log = 'True' AND serial_number LIKE '{}%%' GROUP BY serial_number, test_date, test_type) AS \"Dummy\" ".format(
                blacklist, model)
            minquery = "SELECT MIN (mycount) from (select distinct (COUNT(reading)) as mycount from \"{}\" WHERE in_log = 'True' AND serial_number LIKE '{}%%' GROUP BY serial_number, test_date, test_type) AS \"Dummy\" ".format(
                blacklist, model)

        try:
            min = [x for x in dbms.query_return_all_data(minquery)][0][0]
            max = [x for x in dbms.query_return_all_data(maxquery)][0][0]
            return [min,max]
        except:
            return[0,0]


    def plotbar_err_condition(self, blacklist, low_bound, high_bound, model, x_data,y_data, db):
        self.dbms = backend_database.MyDatabase(backend_database.POSTGRES, dbname=db)


        self.ax = ""
        self.labels = x_data


        x = np.arange(len(self.labels))  # the label locations
        width = 0.30  # the width of the bars

        self.ax = self.subplots()

        self.rects1 = self.ax.bar(x, y_data, width, label="Error Count")
        self.autolabel(self.rects1,1)


        # Add some text for labels, title and custom x-axis tick labels, etc.


        self.ax.set_ylabel('# Of Logs')
        self.ax.set_xlabel('# Of Blacklist in a Log')
        self.ax.set_title('Error Distribution: Model: {} Keyword: {} Error Count From {} to {}'.format(model,blacklist,low_bound,high_bound))
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(self.labels)
        self.ax.legend()
        self.tight_layout()
        plt.show()



    def autolabel(self,rects, num_rec):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for rect in rects:
            height = rect.get_height()

            if num_rec == 1:
                num_rec = 2
            ano_width = rect.get_x()+ rect.get_width()/num_rec
            if num_rec == 3:
                ano_width = ano_width+0.05

            self.ax.annotate('{}'.format(height),
                        xy=(ano_width, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')

    def autolabel_percent(self,rects, num_rec):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for rect in rects:
            height = rect.get_height()

            if num_rec == 1:
                num_rec = 2
            ano_width = rect.get_x()+ rect.get_width()/num_rec
            if num_rec == 3:
                ano_width = ano_width+0.05

            if height == 0.0:
                pass
            else:
                if height > 0.1:
                    height = float(format(height,'.1f'))
                self.ax.annotate(height,
                            xy=(ano_width, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom')


    def plot_h_bar(self, model = '', testtype = '', table1 = "", table2 = "", minx = '', maxx = '', intervalx = '', miny = '', maxy = '', intervaly = ''):
        self.dbms = backend_database.MyDatabase(backend_database.POSTGRES, dbname=model)
        x_interval =np.arange(minx,maxx+intervalx,intervalx)
        y_interval = np.arange(miny, maxy+intervaly, intervaly)
        x_unit = self.dbms.return_unit(table1)
        y_unit = self.dbms.return_unit(table2)

        x_legend = []
        for i, x in enumerate(y_interval):
            if i < len(y_interval)-1:
                x_legend.append(str(y_interval[i])+"-"+str(y_interval[i+1]))
        y_tick = []
        for i, x in enumerate(x_interval):
            if i < len(x_interval)-1:
                y_tick.append(str(x_interval[i])+"-"+str(x_interval[i+1]))

        raw_count = {}
        graph_percentage = {}

        for y in y_tick:
            y_min_max = y.split('-')
            raw_count[y] = []
            for x in x_legend:
                x_min_max = x.split('-')
                if testtype == "All":
                    query = "SELECT COUNT(DISTINCT(\"{table1}\".serial_number)) FROM \"{table1}\" " \
                            "INNER JOIN \"{table2}\"" \
                            "ON \"{table1}\".serial_number = \"{table2}\".serial_number  " \
                            "AND \"{table1}\".ref_line_number = \"{table2}\".ref_line_number " \
                            "AND \"{table1}\".test_date = \"{table2}\".test_date " \
                            "WHERE \"{table1}\".reading IS NOT NULL " \
                            "AND \"{table2}\".reading IS NOT NULL " \
                            "AND \"{table1}\".serial_number LIKE '{model}%%' " \
                            "AND \"{table1}\".reading >= {y_min}" \
                            "AND \"{table1}\".reading < {y_max}" \
                            "AND \"{table2}\".reading >= {x_min}" \
                            "AND \"{table2}\".reading < {x_max}".format(table1=table1, table2=table2,
                                                                        model=model, y_min=y_min_max[0],
                                                                        y_max=y_min_max[1], x_min=x_min_max[0],
                                                                        x_max=x_min_max[1])
                else:
                    query = "SELECT COUNT(DISTINCT(\"{table1}\".serial_number)) FROM \"{table1}\" " \
                                "INNER JOIN \"{table2}\"" \
                                "ON \"{table1}\".serial_number = \"{table2}\".serial_number  " \
                                "AND \"{table1}\".ref_line_number = \"{table2}\".ref_line_number " \
                                "AND \"{table1}\".test_date = \"{table2}\".test_date " \
                                "WHERE \"{table1}\".reading IS NOT NULL " \
                                "AND \"{table2}\".reading IS NOT NULL " \
                                "AND \"{table1}\".serial_number LIKE '{model}%%' " \
                                "AND \"{table1}\".test_type = '{testtype}' " \
                                "AND \"{table1}\".reading >= {y_min}" \
                                "AND \"{table1}\".reading < {y_max}" \
                                "AND \"{table2}\".reading >= {x_min}" \
                                "AND \"{table2}\".reading < {x_max}".format(table1=table1, table2=table2, testtype=testtype,
                                                                          model=model, y_min=y_min_max[0],
                                                                          y_max=y_min_max[1], x_min=x_min_max[0],
                                                                          x_max=x_min_max[1])

                print(query)
                temp = (int(list(self.dbms.query_return_all_data(query))[0][0]))
                raw_count[y].append(temp)
        for key in raw_count:
            total = sum(raw_count[key])
            if total != 0:
                graph_percentage[key] = list(map(lambda x: round(100*x/total,2),raw_count[key]))




        category_names = list(map(lambda x: x+" "+y_unit, x_legend))
        results ={}
        for key in graph_percentage:
            results[key+" "+x_unit] = graph_percentage[key]


        labels = list(results.keys())
        data = np.array(list(results.values()))


        data_cum = data.cumsum(axis=1)
        category_colors = plt.get_cmap('jet')(
            np.linspace(0.15, 0.85, data.shape[1]))

        self.ax = self.subplots()
        self.ax.invert_yaxis()
        self.ax.xaxis.set_visible(False)
        self.ax.set_xlim(0, np.sum(data, axis=1).max())

        for i, (colname, color) in enumerate(zip(category_names, category_colors)):

            widths = data[:, i]
            starts = data_cum[:, i] - widths
            self.ax.barh(labels, widths, left=starts, height=0.5,
                    label=colname, color=color)
            xcenters = starts + widths / 2

            r, g, b, _ = color
            text_color = 'black' if r * g * b < 0.5 else 'black'
            for y, (x, c) in enumerate(zip(xcenters, widths)):
                if c != 0:
                    self.ax.text(x, y, str(c)+'%', ha='center', va='center',
                            color=text_color)


        self.ax.legend(ncol=len(category_names), bbox_to_anchor=(0, 1),
                  loc='lower left', fontsize='small')

        plt.suptitle('Reading Distribution: Model: {}  {} vs {}'.format(model, table1, table2))
        plt.show()

    def plot_line_graph(self, added_list):
        table_list = [x[:-6] for x in added_list]
        self.ax = self.subplots()
        model_list = [x[:6] for x in table_list]

        data = []
        legend_list = []
        avg_list = []

        for idx,table in enumerate(table_list):
            temp_dbms = backend_database.MyDatabase(backend_database.POSTGRES, dbname=model_list[idx])
            temp_data = temp_dbms.return_distict_sensor_reading(table)
            data.append(temp_data)
            avg_list.append(temp_dbms.return_sensor_avg(table))
            if idx == 0:
                min_length = len(temp_data)
                unit = temp_dbms.return_unit_from_graph(table+"_graph")

            if len(temp_data) <= min_length:
                min_length = len(temp_data)


        processed_data = []

        for content in data:
            if len(content) == min_length:
                processed_data.append(content)
            else:

                append_idx = [int(x) for x in np.arange(start = 0, stop = len(content), step = (len(content)/min_length))]


                temp = []
                for idx, val in enumerate(content):
                    if idx in append_idx:
                        temp.append(val)
                processed_data.append(temp)


        for idx, data in enumerate(processed_data):
            temp_plot, = self.ax.plot(np.arange(min_length), data, label=table_list[idx]+" Avg: "+avg_list[idx]+" "+unit)
            legend_list.append(temp_plot)

        self.ax.set_ylabel(unit)
        self.ax.set_xlabel("Number of Reading")
        self.tight_layout()
        self.ax.yaxis.grid(True)

        difference_list = []
        for idx, avg in enumerate(avg_list):
            if idx == 0:
                pass
            else:
                difference_list.append(str(round((float(avg_list[idx])-float(avg_list[idx-1])),2)))
        difference = ','
        difference = difference.join(difference_list)

        red_patch = mpatches.Patch(color='red', label="Difference "+difference+" "+unit)

        legend_list.append(red_patch)
        plt.legend(handles=legend_list)

        self.ax.set_title('Sensor Trends')
        plt.show()


    def plot_single_table_line_graph(self, table, sensor_1, sensor_2, db):
        self.ax = self.subplots()
        # sensor_1 = sensor_1 + "_reading"
        # sensor_2 = sensor_2 + "_reading"
        legend = []

        self.dbms = backend_database.MyDatabase(backend_database.POSTGRES, dbname=db)



        unit = self.dbms.return_unit(sensor_1[:-8:])



        reading1 = [round(float(data),2) for data in self.dbms.return_list_of_column_view(table, sensor_1)]
        reading2 = [round(float(data),2) for data in self.dbms.return_list_of_column_view(table, sensor_2)]

        readingList = []
        for i in range(len(reading1)):
            readingList.append({"sensor1":reading1[i],"sensor2":reading2[i]})

        sortedReadingList = sorted(readingList,key = lambda i: i["sensor1"])

        sorted_x = [x["sensor1"] for x in sortedReadingList]
        sorted_y = [y["sensor2"] for y in sortedReadingList]


        plot_x, = self.ax.plot(np.arange(len(sorted_x)), sorted_x, label=sensor_1)
        plot_y, = self.ax.plot(np.arange(len(sorted_y)), sorted_y, label=sensor_2)
        # plot_dif, = self.ax.plot(np.arange(len(sorted_x)), [i-j for i,j in zip(sorted_x,sorted_y)], label="Difference")
        legend.append(plot_x)
        legend.append(plot_y)
        # legend.append(plot_dif)

        self.ax.set_ylabel(unit)
        self.ax.set_xlabel("Number of Reading (sorted by "+sensor_1+")")
        self.tight_layout()
        self.ax.yaxis.grid(True)
        plt.legend(handles=legend)
        self.ax.set_title('Sensor Relationship')
        plt.show()

    def plot_single_table_line_difference_graph(self, table, sensor_1, sensor_2, db):
        self.ax = self.subplots()
        # sensor_1 = sensor_1 + "_reading"
        # sensor_2 = sensor_2 + "_reading"
        legend = []

        self.dbms = backend_database.MyDatabase(backend_database.POSTGRES, dbname=db)
        unit = self.dbms.return_unit(sensor_1[:-8:])

        reading1 = [round(float(data),2) for data in self.dbms.return_list_of_column_view(table, sensor_1)]
        reading2 = [round(float(data),2) for data in self.dbms.return_list_of_column_view(table, sensor_2)]

        readingList = []
        for i in range(len(reading1)):
            readingList.append({"sensor1":reading1[i],"sensor2":reading2[i]})

        sortedReadingList = sorted(readingList,key = lambda i: i["sensor1"])

        sorted_x = [x["sensor1"] for x in sortedReadingList]
        sorted_y = [y["sensor2"] for y in sortedReadingList]


        plot_dif, = self.ax.plot(np.arange(len(sorted_x)), [i-j for i,j in zip(sorted_x,sorted_y)], label="Difference")
        legend.append(plot_dif)

        self.ax.set_ylabel(unit)
        self.ax.set_xlabel("Number of Reading (sorted by "+sensor_1+")")
        self.tight_layout()
        self.ax.yaxis.grid(True)
        plt.legend(handles=legend)
        self.ax.set_title('Sensor Value Difference')
        plt.show()



# dbms = backend_database.MyDatabase(backend_database.POSTGRES, dbname="FGT60F")
# fig1 = plt.figure(FigureClass=graphFigure)
# fig1.plot_single_table_line_graph("Temp_Horizontal_MAX","CPU ON-DIE thermal sensor","PHY B50182 temp sensor", "FGT60F")
# fig2 = plt.figure(FigureClass=graphFigure)
# fig2.plot_single_table_line_difference_graph("Temp_Horizontal_MAX","CPU ON-DIE thermal sensor","PHY B50182 temp sensor", "FGT60F")
#

#fig1.plotbar(["lol_graph","uwu_graph"])



#fig2 = plt.figure(FigureClass=graphFigure, figtitle='m222y title')
#fig2.plotbar("+VCC3_Customized_graph")

#plt.close(fig2)
#plt.show()




