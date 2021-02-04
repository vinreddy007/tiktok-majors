import pandas
import chart_studio
import plotly.express as px

username = 'Bensimmons'
api_key = 'QG5xO4ovbCu7rHwjl22x'
chart_studio.tools.set_credentials_file(username=username, api_key=api_key)


class Cols:
    LIKES = 'Likes'
    MAJOR = 'Major'
    GENDER = 'Gender specified'
    SALARY = 'Salary'
    DEGREES_AWARDED = 'Degrees Awarded'


#####################
# 0. Process Comments
#####################

df = pandas.read_csv('../data/tiktok_comments.csv')

# add one to likes, since the commenter also 'likes' that major
df[Cols.LIKES] += 1

# drop unneeded columns
df = df.drop(['Comment', 'More information'], axis=1)

# create new rows when multiple majors are specified
df = pandas.concat([pandas.Series(row[Cols.LIKES], row[Cols.MAJOR].split(','))
                    for _, row in df.iterrows()]).reset_index()
df = df.rename(columns={"index": Cols.MAJOR, 0: Cols.LIKES})

# remove leading space
df[Cols.MAJOR] = df[Cols.MAJOR].apply(lambda x: x.lstrip())

# group by Major and sort from most to least likes
df = df.groupby(Cols.MAJOR)[Cols.LIKES].sum().sort_values(ascending=False)


#############################################
# 1. Plot bar chart of most attractive majors
#############################################

top_majors = df[:15]

fig = px.bar(top_majors)
fig.update_layout(yaxis_title=Cols.LIKES, showlegend=False)
# fig.show()
chart_studio.plotly.plot(fig, filename="most_attractive_majors", auto_open=True)


###################################################
# 2. Plot scatter chart of Salary vs Attractiveness
# https://www.kaggle.com/wsj/college-salaries
###################################################

salaries = pandas.read_csv('../data/degree_salaries.csv')
salaries = salaries[[Cols.MAJOR, Cols.SALARY]]
salaries = salaries.set_index(Cols.MAJOR)

# convert salary from string to float
salaries[Cols.SALARY] = salaries[Cols.SALARY].apply(lambda x: float(x.strip('$').replace(',', '')))

# convert df from series to dataframe so that you can join with salaries
df = pandas.DataFrame(df)
salaries = df.join(salaries, on=Cols.MAJOR).dropna()
top_ten = salaries[:10]

fig = px.scatter(top_ten.reset_index(), x=Cols.SALARY, y=Cols.LIKES,
                 hover_name=Cols.MAJOR, text=Cols.MAJOR, size=Cols.SALARY, trendline="ols")
fig.update_traces(textposition='bottom center')
# fig.show()
chart_studio.plotly.plot(fig, filename="attractiveness_vs_salary_majors", auto_open=True)


#############################################################
# 3. Plot scatter chart of Major Popularity vs Attractiveness
# https://www.niche.com/blog/the-most-popular-college-majors/
#############################################################

popular_majors = pandas.read_csv('../data/popular_majors.csv', sep=',', thousands=',')
popular_majors = popular_majors.join(df, on=Cols.MAJOR).dropna()

# manually add text annotation so there aren't so many that they overlap
fig = px.scatter(popular_majors, x=Cols.DEGREES_AWARDED, y=Cols.LIKES,
                 size=Cols.DEGREES_AWARDED,
                 hover_name=Cols.MAJOR, trendline="ols",
                 text=['Nursing', 'Psychology', 'Biology', 'Engineering',
                       'Education', 'Computer Science', 'English',
                       'Economics', None, None, None, None, None, None, None, None, None])
fig.update_traces(textposition='bottom center')
# fig.show()
chart_studio.plotly.plot(fig, filename="attractiveness_vs_degrees_awarded", auto_open=True)
