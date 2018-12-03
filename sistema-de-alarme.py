from flask import  Flask, render_template, redirect, url_for
import RPi.GPIO as gpio
import time, datetime
app = Flask(__name__)

# Pinagem
sirene = 35
ativo = 37
btn_ativo = 33
btn_zona1 = 36
btn_zona2 = 38
btn_zona3 = 40

# Defaults
configuracao_inicial = 1
estado_sistema = 0
configuracao_zona1 = 1
configuracao_zona2 = 1
configuracao_zona3 = 1
estado_zona1 = 0
estado_zona2 = 0
estado_zona3 = 0
logs = []

def setup():
    gpio.setmode(gpio.BOARD)
    gpio.setwarnings(False)

    gpio.setup(ativo, gpio.OUT)
    gpio.setup(sirene, gpio.OUT)
    gpio.setup(btn_ativo, gpio.IN)
    gpio.setup(btn_zona1, gpio.IN)
    gpio.setup(btn_zona2, gpio.IN)
    gpio.setup(btn_zona3, gpio.IN)

    gpio.add_event_detect(btn_ativo, gpio.RISING, bouncetime = 300)
    gpio.add_event_detect(btn_zona1, gpio.RISING, bouncetime = 300)
    gpio.add_event_detect(btn_zona2, gpio.RISING, bouncetime = 300)
    gpio.add_event_detect(btn_zona3, gpio.RISING, bouncetime = 300)

setup()

def agora():
    now = datetime.datetime.now()
    timeString = now.strftime("%Y-%m-%d %H:%M")
    return timeString

@app.route("/")
def index():
    global configuracao_zona1, configuracao_zona2, configuracao_zona3, estado_sistema, \
        estado_zona1, estado_zona2, estado_zona3, btn_zona1, btn_zona2, btn_zona3, sirene, \
        ativo, btn_ativo, configuracao_inicial, logs

    with open('log.txt') as f:
        logs = [x.strip().split(';') for x in f.readlines()]
        f.close()

    if gpio.event_detected(btn_ativo):
        if estado_sistema:
            estado_sistema = 0
            return redirect('desativaSistema')
        else:
            estado_sistema = 1
            return redirect('ativaSistema')
    
    templateData = {
        'message': 'Sistema Ativado',
        'time': agora(),
        'configuracao_zona1': configuracao_zona1,
        'configuracao_zona2': configuracao_zona2,
        'configuracao_zona3': configuracao_zona3,
        'estado_sistema': estado_sistema,
        'configuracao_inicial': configuracao_inicial,
        'estado_zona1': estado_zona1,
        'estado_zona2': estado_zona2,
        'estado_zona3': estado_zona3,
        'logs': logs

    }
    return render_template('main.html', **templateData)

@app.route("/limpaRPi")
def limpaRPi():
    global configuracao_zona1, configuracao_zona2, configuracao_zona3, estado_sistema, \
        estado_zona1, estado_zona2, estado_zona3, btn_zona1, btn_zona2, btn_zona3, sirene, \
        ativo, btn_ativo, configuracao_inicial, logs
    gpio.cleanup()
    setup()
    gpio.output(ativo, 0)
    gpio.output(sirene, 0)

    with open('log.txt') as f:
        logs = [x.strip().split(';') for x in f.readlines()]
        f.close()

    templateData = {
        'message': 'Limpando o sistema',
        'time': agora(),
        'configuracao_zona1': configuracao_zona1,
        'configuracao_zona2': configuracao_zona2,
        'configuracao_zona3': configuracao_zona3,
        'estado_sistema': estado_sistema,
        'configuracao_inicial': configuracao_inicial,
        'estado_zona1': estado_zona1,
        'estado_zona2': estado_zona2,
        'estado_zona3': estado_zona3,
        'logs': logs
    }
    return render_template('main.html', **templateData)

@app.route("/ativaSistema")
def ativaSistema():
    global configuracao_zona1, configuracao_zona2, configuracao_zona3, estado_sistema, \
        estado_zona1, estado_zona2, estado_zona3, btn_zona1, btn_zona2, btn_zona3, sirene, \
        ativo, btn_ativo, configuracao_inicial, logs

    configuracao_inicial = 0
    estado_sistema = 1
    gpio.output(ativo, 1)

    if gpio.event_detected(btn_ativo):
        if estado_sistema == 1:
            estado_sistema = 0
            return redirect('desativaSistema')
                
    if gpio.event_detected(btn_zona1) and configuracao_zona1:
        gpio.output(sirene, 1)
        estado_zona1 = 1

    if gpio.event_detected(btn_zona2) and configuracao_zona2:
        gpio.output(sirene, 1)
        estado_zona2 = 1
        
    if gpio.event_detected(btn_zona3) and configuracao_zona3:
        gpio.output(sirene, 1)
        estado_zona3 = 1

    with open('log.txt', 'a') as f:
        if estado_zona1 or estado_zona2 or estado_zona3:
            f.write(agora() + ';' + str(estado_zona1) + ';' + str(estado_zona2) + ';' + str(estado_zona3) + '\n')
        f.close()

    with open('log.txt') as f:
        logs = [x.strip().split(';') for x in f.readlines()]
        f.close()
    
    templateData = {
        'message': 'Sistema Ativado',
        'time': agora(),
        'configuracao_zona1': configuracao_zona1,
        'configuracao_zona2': configuracao_zona2,
        'configuracao_zona3': configuracao_zona3,
        'estado_sistema': estado_sistema,
        'configuracao_inicial': configuracao_inicial,
        'estado_zona1': estado_zona1,
        'estado_zona2': estado_zona2,
        'estado_zona3': estado_zona3,
        'logs': logs
    }

    return render_template('main.html', **templateData)

@app.route("/desativaSistema")
def desativaSistema():
    global configuracao_zona1, configuracao_zona2, configuracao_zona3, estado_sistema, \
        estado_zona1, estado_zona2, estado_zona3, btn_zona1, btn_zona2, btn_zona3, sirene, \
        ativo, btn_ativo, configuracao_inicial, logs

    # gpio.cleanup()
    # setup()
    
    estado_sistema = 0
    configuracao_inicial = 1
    gpio.output(ativo, 0)
    gpio.output(sirene, 0)
    estado_zona1 = 0
    estado_zona2 = 0
    estado_zona3 = 0

    with open('log.txt') as f:
        logs = [x.strip().split(';') for x in f.readlines()]
        f.close()

    if gpio.event_detected(btn_ativo):
        if estado_sistema == 0:
            estado_sistema = 1
            return redirect('ativaSistema')
        
    templateData = {
        'message': 'Sistema Desativado',
        'time': agora(),
        'configuracao_zona1': configuracao_zona1,
        'configuracao_zona2': configuracao_zona2,
        'configuracao_zona3': configuracao_zona3,
        'estado_sistema': estado_sistema,
        'configuracao_inicial': configuracao_inicial,
        'estado_zona1': estado_zona1,
        'estado_zona2': estado_zona2,
        'estado_zona3': estado_zona3,
        'logs': logs
    }
    return render_template('main.html', **templateData)

def render():
    global configuracao_zona1, configuracao_zona2, configuracao_zona3, estado_sistema, \
        estado_zona1, estado_zona2, estado_zona3, btn_zona1, btn_zona2, btn_zona3, sirene, \
        ativo, btn_ativo, configuracao_inicial, logs
   
    with open('log.txt') as f:
        logs = [x.strip().split(';') for x in f.readlines()]
        f.close()

    if gpio.event_detected(btn_ativo):
        if estado_sistema:
            estado_sistema = 0
            return redirect('desativaSistema')
        else:
            estado_sistema = 1
            return redirect('ativaSistema')

    templateData = {
        'estado_sistema': estado_sistema,
        'configuracao_inicial': configuracao_inicial,
        'configuracao_zona1': configuracao_zona1,
        'configuracao_zona2': configuracao_zona2,
        'configuracao_zona3': configuracao_zona3,
        'estado_zona1': estado_zona1,
        'estado_zona2': estado_zona2,
        'estado_zona3': estado_zona3,
        'logs': logs
    }
    return render_template('main.html', **templateData)

@app.route("/desativaZona1")
def desativaZona1():
    global configuracao_zona1

    if configuracao_zona1:
        configuracao_zona1 = 0
        return redirect('/')
    else:
        configuracao_zona1 = 1
        return redirect('/')

    global configuracao_zona1, configuracao_zona2, configuracao_zona3, estado_sistema, \
        estado_zona1, estado_zona2, estado_zona3, btn_zona1, btn_zona2, btn_zona3, sirene, \
        ativo, btn_ativo, configuracao_inicial, logs
   
    with open('log.txt') as f:
        logs = [x.strip().split(';') for x in f.readlines()]
        f.close()

    if gpio.event_detected(btn_ativo):
        if estado_sistema:
            estado_sistema = 0
            return redirect('desativaSistema')
        else:
            estado_sistema = 1
            return redirect('ativaSistema')

    templateData = {
        'estado_sistema': estado_sistema,
        'configuracao_inicial': configuracao_inicial,
        'configuracao_zona1': configuracao_zona1,
        'configuracao_zona2': configuracao_zona2,
        'configuracao_zona3': configuracao_zona3,
        'estado_zona1': estado_zona1,
        'estado_zona2': estado_zona2,
        'estado_zona3': estado_zona3,
        'logs': logs
    }
    return render_template('main.html', **templateData)


@app.route("/desativaZona2")
def desativaZona2():
    global configuracao_zona2

    if configuracao_zona2:
        configuracao_zona2 = 0
        return redirect('/')
    else:
        configuracao_zona2 = 1
        return redirect('/')
    
    global configuracao_zona1, configuracao_zona2, configuracao_zona3, estado_sistema, \
        estado_zona1, estado_zona2, estado_zona3, btn_zona1, btn_zona2, btn_zona3, sirene, \
        ativo, btn_ativo, configuracao_inicial, logs
   
    with open('log.txt') as f:
        logs = [x.strip().split(';') for x in f.readlines()]
        f.close()

    if gpio.event_detected(btn_ativo):
        if estado_sistema:
            estado_sistema = 0
            return redirect('desativaSistema')
        else:
            estado_sistema = 1
            return redirect('ativaSistema')

    templateData = {
        'estado_sistema': estado_sistema,
        'configuracao_inicial': configuracao_inicial,
        'configuracao_zona1': configuracao_zona1,
        'configuracao_zona2': configuracao_zona2,
        'configuracao_zona3': configuracao_zona3,
        'estado_zona1': estado_zona1,
        'estado_zona2': estado_zona2,
        'estado_zona3': estado_zona3,
        'logs': logs
    }
    return render_template('main.html', **templateData)


@app.route("/desativaZona3")
def desativaZona3():
    global configuracao_zona3

    if configuracao_zona3:
        configuracao_zona3 = 0
        return redirect('/')
    else:
        configuracao_zona3 = 1
        return redirect('/')

    global configuracao_zona1, configuracao_zona2, configuracao_zona3, estado_sistema, \
        estado_zona1, estado_zona2, estado_zona3, btn_zona1, btn_zona2, btn_zona3, sirene, \
        ativo, btn_ativo, configuracao_inicial, logs
   
    with open('log.txt') as f:
        logs = [x.strip().split(';') for x in f.readlines()]
        f.close()

    if gpio.event_detected(btn_ativo):
        if estado_sistema:
            estado_sistema = 0
            return redirect('desativaSistema')
        else:
            estado_sistema = 1
            return redirect('ativaSistema')

    templateData = {
        'estado_sistema': estado_sistema,
        'configuracao_inicial': configuracao_inicial,
        'configuracao_zona1': configuracao_zona1,
        'configuracao_zona2': configuracao_zona2,
        'configuracao_zona3': configuracao_zona3,
        'estado_zona1': estado_zona1,
        'estado_zona2': estado_zona2,
        'estado_zona3': estado_zona3,
        'logs': logs
    }
    return render_template('main.html', **templateData)

if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host='0.0.0.0', port = 80, debug=True)
