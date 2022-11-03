from flask import Flask, render_template, request, session
import json
import plotly
import pandas as pd
import os
import pickle
import plotly.graph_objects as go

app = Flask(__name__)
app.secret_key = "123"

DATA_PATH = os.path.join(os.path.dirname(__file__), "static", "data");
MODELS_PATH = os.path.join(os.path.dirname(__file__), "static", "models");

users = [
    {"username" : "user1" , "password" : "user1"},
    {"username" : "user2" , "password" : "user2"},
    {"username" : "user3" , "password" : "user3"},
    {"username" : "user4" , "password" : "user4"},
    {"username" : "user5" , "password" : "user5"},
]


@app.route("/", methods=['GET' , 'POST'])
def landingpage():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # if(username == "admin" and password == "admin123"):
        for user in users:
            if(username == user['username'] and password == user['password']):
                session['username'] = username
                return render_template("index.html", username=session['username'])
        else:
            return render_template("login.html", msg="Invalid Credentials!")
    else:
        return render_template("login.html")

@app.route("/logout", methods=['GET' , 'POST'])
def logout():
    session.pop('username', None)
    return render_template("login.html")


@app.route("/home", methods=['GET' , 'POST'])
def home():
    if request.method == 'POST' and session['username'] != None:
        # getting selected stock name
        stock = request.form['stockname']

        # reading data
        data = pd.read_csv(DATA_PATH + "\\"+ stock+".csv")
        data=data.rename(columns={"Date": "ds", "Close": "y"})

        # splitting 80 : 20 into train_data and test_data
        split = int(len(data)*80/100)
        train_data=data[0:split]
        test_data=data[split:]

        # loading prophet model
        model = pickle.load(open( MODELS_PATH +'\\'+ stock+"_model.pkl", 'rb'))

        # forecasting data
        forecast = model.predict(test_data)


        # saving plot
        # fig2 =model.plot(forecast)
        # fig2.savefig('prophetplot.png')

        # Creating interactive plot
        fig1 = go.Figure([
            go.Scatter(
                name='Close Price',
                x=train_data['ds'],
                y=round(train_data['y'], 2),
                mode='lines',
                line=dict(color='rgb(31, 119, 180)'),
                showlegend=False
            ),
            go.Scatter(
                name='Actual Price',
                x=test_data['ds'],
                y=round(test_data['y'], 2),
                mode='lines',
                line=dict(color='rgb(255, 0, 0)'),
            ),
            go.Scatter(
                name='Predicted Price',
                x=forecast['ds'],
                y=round(forecast['yhat'], 2),
                mode='lines',
                line=dict(color='rgb(46, 184, 46)'),
            ),
            go.Scatter(
                name='95% CI Upper',
                x=forecast['ds'],
                y=round(forecast['yhat_upper'], 2),
                mode='lines',
                marker=dict(color='#444'),
                line=dict(width=0),
                showlegend=False
            ),
            go.Scatter(
                name='95% CI Lower',
                x=forecast['ds'],
                y=round(forecast['yhat_lower'], 2),
                marker=dict(color='#444'),
                line=dict(width=0),
                mode='lines',
                fillcolor='rgba(68, 68, 68, 0.3)',
                fill='tonexty',
                showlegend=False
            )
        ])
        fig1.update_layout(
            xaxis_title='Date',
            yaxis_title= 'Close Price',
            title= stock +' Stock Price Prediction for 3 Months',
            template='plotly_dark',
            hovermode='x'
        )
        fig1.update_yaxes(rangemode='tozero')

        # Jsonify the plot and send it to the UI
        graphJSON1 = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
        
        
        return render_template("index.html", stock=stock, graphJSON1=graphJSON1 , username=session['username'] )
    else:
        return render_template("index.html", username=session['username'])


if __name__ == '__main__':
    app.run(debug=True)
