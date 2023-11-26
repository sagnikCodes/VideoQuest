from website import create_app

app = create_app()


if __name__ == "__main__":
    app.run(debug=True, port=9000)
    # app.run(host='0.0.0.0', port=9000)