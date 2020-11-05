from random import random
from bokeh.models import ColumnDataSource

from bokeh.layouts import column
from bokeh.models import Button,CustomJS, DatePicker,Div
from bokeh.palettes import RdYlBu3,Category20c
from bokeh.plotting import figure, curdoc, show, output_file
from bokeh.transform import cumsum
import pandas as pd 
from bokeh.layouts import gridplot,layout


data = pd.read_csv("https://raw.githubusercontent.com/datadesk/california-coronavirus-data/master/cdph-positive-test-rate.csv")
data['date'] = pd.to_datetime(data['date'])
data_race = pd.read_csv('https://raw.githubusercontent.com/datadesk/california-coronavirus-data/master/cdph-race-ethnicity.csv')
data_race['date'] = pd.to_datetime(data_race['date'])

last_update_date = data_race.iloc[1,0]
header = Div(text="""The data used in this dashboard was collected by 'Los Angeles Times Data and Graphics Department'.
The race-ethnicity data was retrieved from California Department of Public Health. A forked repo can be found at url:https://github.com/alvinzhou66/california-coronavirus-data/blob/master/cdph-race-ethnicity.csv.
<b>Last updated on:{}</b>""".format(last_update_date),
width=800, height=60)

date_picker = DatePicker(title='Select date', value="2020-08-15", min_date="2020-08-01", max_date="2020-08-31")
curr_date = pd.to_datetime(date_picker.value)

date_picker2 = DatePicker(title='Select date', value="2020-08-16", min_date="2020-05-14", max_date="2020-11-02")
curr_date2 = pd.to_datetime(date_picker2.value)

data_aug = data[(data["date"]>="2020-08-01") & (data["date"]<"2020-09-01")]
output_file("datetime.html")
p = figure(x_axis_type="datetime",title="Corona info in California",x_axis_label='date', y_axis_label='number of cases',plot_width=500, plot_height=400)
r = p.text(x=[curr_date], y=[data[data["date"] == curr_date]["confirmed_cases"]], text=[str(data[data["date"] == curr_date]["confirmed_cases"].values[0])], text_color=["red"], text_font_size="16px",text_baseline="middle", text_align="center")
p.line(data_aug["date"],data_aug["confirmed_cases"], color='navy', alpha=0.5,legend_label="confirmed_cases")


def get_data(curr_date2,data_race,agg_feat):
    data_agg = data_race[data_race["date"] == curr_date2].groupby(by = ["race"])[agg_feat].agg("sum").reset_index(name='value')
    data_agg['angle'] = data_agg['value'] / data_agg['value'].sum() * 2*3.14
    data_agg['color'] = Category20c[len(data_agg.values)]
    data_agg['percentage'] = (data_agg['value'] / data_agg['value'].sum())*100
    return data_agg

data_agg = get_data(curr_date2,data_race,"confirmed_cases_total")
p_pie = figure(plot_height=350, title="percentage of confirmed case by race", toolbar_location=None,tools="hover", tooltips="@race: @percentage", x_range=(-0.5, 1.0))
pie = p_pie.wedge(x=0, y=1, radius=0.3,
        start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
        line_color="white", fill_color='color', legend_field='race', source=data_agg)
p_pie.axis.axis_label=None
p_pie.axis.visible=False
p_pie.grid.grid_line_color = None


data_death = get_data(curr_date2,data_race,"deaths_total")
p_death = figure(plot_height=350, title="percentage of death case by race", toolbar_location=None,tools="hover", tooltips="@race: @percentage", x_range=(-0.5, 1.0))
pie_death = p_death.wedge(x=0, y=1, radius=0.3,
        start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
        line_color="white", fill_color='color', legend_field='race', source=data_death)
p_death.axis.axis_label=None
p_death.axis.visible=False
p_death.grid.grid_line_color = None

data_pop = get_data(curr_date2,data_race,"population_percent")
p_pop = figure(plot_height=350, title="percentage of total population by race", toolbar_location=None,tools="hover", tooltips="@race: @percentage", x_range=(-0.5, 1.0))
pie_pop = p_pop.wedge(x=0, y=1, radius=0.3,
        start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
        line_color="white", fill_color='color', legend_field='race', source=data_pop)
p_pop.axis.axis_label=None
p_pop.axis.visible=False
p_pop.grid.grid_line_color = None

ds = r.data_source
def callback(attr, old, new):
    new_data = {}
    date = pd.to_datetime(date_picker.value)
    new_data["x"] = [date]
    new_data["y"] = [data[data["date"] == date]["confirmed_cases"]]
    new_data['text_color'] = ["red"]
    new_data['text'] = [str(data[data["date"] == date]["confirmed_cases"].values[0])]
    ds.data = new_data

ds_pie = pie.data_source
ds_death = pie_death.data_source
ds_pop = pie_pop.data_source
def callback_pie(attr, old, new):
    date = pd.to_datetime(date_picker2.value)
    new_data = get_data(date,data_race,"confirmed_cases_total")
    new_data_death = get_data(date,data_race,"deaths_total")
    new_data_pop = get_data(date,data_race,"population_percent")
    ds_pie.data = new_data
    ds_death.data = new_data_death
    ds_pop.data = new_data_pop


date_picker.on_change("value", callback)
date_picker2.on_change("value", callback_pie)

# grid = gridplot([[date_picker, p], [date_picker2, p_pie],[None,p_death]])

# curdoc().add_root(column(p,date_picker,p_pie,date_picker2,p_death))

curdoc().add_root(layout([[header],
    [date_picker, p],
    [date_picker2],
    [p_pie,p_death,p_pop]]))
# show(p_pie)

# # create a plot and style its properties
# p = figure(x_range=(0, 100), y_range=(0, 100), toolbar_location=None)
# p.border_fill_color = 'black'
# p.background_fill_color = 'black'
# p.outline_line_color = None
# p.grid.grid_line_color = None

# # add a text renderer to our plot (no data yet)
# r = p.text(x=[], y=[], text=[], text_color=[], text_font_size="26px",
#            text_baseline="middle", text_align="center")

# i = 0

# ds = r.data_source

# # create a callback that will add a number in a random location
# def callback():
#     global i

#     # BEST PRACTICE --- update .data in one step with a new dict
#     new_data = dict()
#     new_data['x'] = ds.data['x'] + [random()*70 + 15]
#     new_data['y'] = ds.data['y'] + [random()*70 + 15]
#     new_data['text_color'] = ds.data['text_color'] + [RdYlBu3[i%3]]
#     new_data['text'] = ds.data['text'] + [str(i)]
#     ds.data = new_data

#     i = i + 1

# # add a button widget and configure with the call back
# button = Button(label="Press Me")
# button.on_click(callback)

# # put the button and plot in a layout and add to the document
# curdoc().add_root(column(button, p))