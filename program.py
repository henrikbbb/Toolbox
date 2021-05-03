from tkinter import *
from tkinter import ttk
from tkinter import filedialog, messagebox
import numpy as np
import pandas as pd
import os
import random
from sklearn import svm

# pages

def page_start():
    window.title("Toolbox")
    window.geometry("600x500")
    frame = Frame(window)
    frame.pack()
    Button(frame, text = "neues Projekt", command = lambda: [page_createProject(), frame.destroy()]).pack()
    # Button(frame, text = "Projekt öffnen").pack()
    # Button(frame, text = "Anleitung").pack()

def page_createProject():
    window.title("neues Projekt")
    frame = Frame(window)
    frame.pack()
    Button(frame, text = "zurück", command = lambda: [page_start(), frame.destroy()]).pack()
    Label(frame, text = "Name wählen").pack()
    eName = Entry(frame)
    eName.pack()
    Label(frame, text = "Art wählen").pack()
    types = [
        ("Standard", 1),
        ("Erkennung falscher Daten", 2)
    ]
    type = IntVar()
    type.set(1)
    for text, value in types:
        Radiobutton(frame, text = text, variable = type, value = value).pack(anchor = W)
    commandError = lambda: messagebox.showerror(title = None, message = "Kein Name angegeben")
    command = lambda: [project.setup(eName.get(), type.get(), [], {}), page_project(), frame.destroy()]
    Button(frame, text = "ok", command = lambda: [commandError() if eName.get() == "" else command()]).pack()

def page_project():
    window.title(project.name)
    frame = Frame(window)
    frame.pack()
    # Button(frame, text = "Menu", command = lambda: [page_start(), frame.destroy()]).pack()
    frameClasses = LabelFrame(frame, text = "Klassen")
    frameClasses.pack()
    def showClass(frame, parent, className):
        labelText = className + " (0)"
        if className in project.data:
            labelText = className + " (" + str(len(project.data[className])) + ")"

        labelFrame = LabelFrame(parent, text = labelText, bd = 0)
        labelFrame.pack(anchor = W)

        command = lambda: [project.setData(loadData("Messwerte wählen"), className), frame.destroy(), page_project()]
        Button(labelFrame, text = "importieren", command = command).pack(side = LEFT)

        return labelFrame
    if project.type == 2:
        showClass(frame, frameClasses, "echte Messwerte")
        labelFrame = showClass(frame, frameClasses, "gefälschte Messwerte")

        state = "normal" if "echte Messwerte" in project.data and len(project.data["echte Messwerte"]) > 0 else "disabled"
        command = lambda: [frame.destroy(), page_createXValues()]
        Button(labelFrame, text = "falsche Messwerte erstellen", state = state, command = command).pack(side = LEFT)

        state = "normal" if createdFakeData else "disabled"
        command = lambda: [exportData(project.data["gefälschte Messwerte"], "gefälschte Messwerte")]
        Button(labelFrame, text = "exportieren", state = state, command = command).pack(side = LEFT)
    else:
        for className in project.classNames:
            showClass(frame, frameClasses, className)
        ttk.Separator(frameClasses, orient = HORIZONTAL).pack(fill = 'x', pady = 5)
        Button(frameClasses, text = "neue Klasse erstellen", command = lambda: [frame.destroy(), page_createClass()]).pack()

    text = "Modell" if project.accuracy == None else "Modell (ca. " + str(round(100*project.accuracy)) + "% Genauigkeit)"
    frameModel = LabelFrame(frame, text = text)
    frameModel.pack()

    state = "normal" if project.trainable() else "disabled"
    Button(frameModel, text = "Modell trainieren", state = state, command = lambda: [project.train(), frame.destroy(), page_project()]).pack()
    state = "normal" if project.classifier != None else "disabled"
    Button(frameModel, text = "Messwerte testen", state = state, command = lambda: [project.test(loadData("Messwerte wählen"))]).pack()

def page_createClass():
    window.title("Klasse erstellen")
    frame = Frame(window)
    frame.pack()
    Label(frame, text = "Titel wählen").pack()
    eName = Entry(frame)
    eName.pack()
    commandError = lambda: messagebox.showerror(title = None, message = "Kein Name angegeben")
    command = lambda: [project.addClass(eName.get()), frame.destroy(), page_project()]
    Button(frame, text = "Klasse erstellen", command = lambda: [commandError() if eName.get() == "" else command()]).pack()

def page_createXValues():
    length = len(project.data["echte Messwerte"][0])

    def checkXValues(list):
        for i in range(len(list)):
            value = list[i]
            value = value.replace(".", "")
            # empty entrys?
            if len(value) == 0:
                messagebox.showerror(title = None, message = "Es sind nicht alle x-Werte eingetragen!")
                return False
            # non-numeric entrys?
            if not value.isnumeric():
                messagebox.showerror(title = None, message = "Es sind nicht alle x-Werte numerisch!")
                return False
        # double values?
        for i in range(len(list) - 1):
            value1 = list[i]
            for j in range(i + 1, len(list)):
                value2 = list[j]
                if value1 == value2:
                    messagebox.showerror(title = None, message = "Es gibt identische x-Werte!")
                    return False
        return True

    def setXValues(frame, option):
        frameEntry = frame.nametowidget(".frame.frameEntry")
        frameEntry.destroy()
        frameEntry = Frame(frame, name = "frameEntry")
        frameEntry.pack()
        if option == 1:
            command = lambda: [setupDatarow(np.arange(length)), frame.destroy(), page_createFakeData()]
        elif option == 2:
            command = lambda: [setupDatarow(np.arange(1, length + 1)), frame.destroy(), page_createFakeData()]
        elif option == 3:
            eStart = Entry(frameEntry)
            eStart.pack()
            commandSuccess = lambda: [setupDatarow(np.arange(float(eStart.get()), length + float(eStart.get()))), frame.destroy(), page_createFakeData()]
            command = lambda: [commandSuccess() if checkXValues([eStart.get()]) else None]
        elif option == 4:
            list = []
            for i in range(length):
                e = Entry(frameEntry)
                list.append(e)
                e.pack()
            def getList():
                xValues = []
                for i in range(length):
                    value = list[i].get()
                    xValues.append(value)
                return xValues
            commandSuccess = lambda: [setupDatarow(np.array([float(i) for i in getList()])), frame.destroy(), page_createFakeData()]
            command = lambda: [commandSuccess() if checkXValues(getList()) else None]
        Button(frameEntry, text = "weiter", command = command).pack()

    window.title("x-Werte eingeben")
    frame = Frame(window, name = "frame")
    frame.pack()
    frameRadiobutton = Frame(frame)
    frameRadiobutton.pack()
    frameEntry = Frame(frame, name = "frameEntry")
    frameEntry.pack()

    Radiobutton(frameRadiobutton, text = "0, 1, 2, ...", value = 1, command = lambda: setXValues(frame, 1)).pack(anchor = W)
    Radiobutton(frameRadiobutton, text = "1, 2, 3, ...", value = 2, command = lambda: setXValues(frame, 2)).pack(anchor = W)
    Radiobutton(frameRadiobutton, text = "aufsteigend um 1", value = 3, command = lambda: setXValues(frame, 3)).pack(anchor = W)
    Radiobutton(frameRadiobutton, text = "benutzerdefiniert", value = 4, command = lambda: setXValues(frame, 4)).pack(anchor = W)

def page_createFakeData():
    window.title("gefälschte Daten erstellen")
    frame = Frame(window)
    frame.pack()

    button = Button(frame, text = "zurück zur Projektübersicht", command = lambda: [frame.destroy(), page_project()])
    button.grid(row = 0)

    canvas = Canvas(frame, bg = "white")
    canvas.grid(row = 1)

    width = 600
    height = 400
    canvas.config(width = width, height = height)

    xLeft = 75
    xRight = width - 50
    yDown = height - 50
    yUp = 25
    draw(canvas, width, height, xLeft, xRight, yDown, yUp)

    def click(event):
        for i in range(len(datarow.yValues)):
            if (np.isnan(datarow.yValues[i])):
                x = mapValue(datarow.xValues[i], datarow.minX, datarow.maxX, xLeft, xRight)
                if (abs(x - event.x) < 10):
                    y = mapValue(event.y, yDown, yUp, datarow.minY, datarow.maxY)
                    datarow.yValues[i] = y
                    if datarow.complete():
                        project.addData(datarow.yValues, "gefälschte Messwerte")
                        setupDatarow(datarow.xValues)
                        global createdFakeData
                        createdFakeData = True
                    draw(canvas, width, height, xLeft, xRight, yDown, yUp)
                    return

    def hover(event):
        canvas.delete("clear")
        for i in range(len(datarow.yValues)):
            if (np.isnan(datarow.yValues[i])):
                x = mapValue(datarow.xValues[i], datarow.minX, datarow.maxX, xLeft, xRight)
                if (abs(x - event.x) < 10):
                    isHovering = True
                    y = event.y
                    r = 3
                    canvas.create_oval(x - r, y - r, x + r, y + r, fill = "red", tag = "clear")
                    return

    canvas.bind("<Button-1>", click)
    canvas.bind("<Motion>", hover)

# functions

def draw(canvas, width, height, xLeft, xRight, yDown, yUp):
    # clear background
    canvas.create_rectangle(0, 0, width, height, fill = "white", outline = "white")
    # axis
    edge = 10
    canvas.create_line(xLeft - edge, yDown + edge, xRight + edge, yDown + edge, fill = "black", width = 2)
    canvas.create_line(xLeft - edge, yDown + edge, xLeft - edge, yUp - edge, fill = "black", width = 2)
    for v in datarow.xValues:
        x = mapValue(v, datarow.minX, datarow.maxX, xLeft, xRight)
        canvas.create_line(x, yDown + edge, x, yDown + edge + 5, fill = "black", width = 2)
        canvas.create_text(x, yDown + edge + 15, text = str(v), fill = "black")
    canvas.create_line(xLeft - edge, yDown, xLeft - edge - 5, yDown, fill = "black", width = 2)
    canvas.create_text(xLeft - edge - 10, yDown, text = str(round(datarow.minY, 1)), fill= "black", anchor = E)
    canvas.create_line(xLeft - edge, yUp, xLeft - edge - 5, yUp, fill = "black", width = 2)
    canvas.create_text(xLeft - edge - 10, yUp, text = str(round(datarow.maxY, 1)), fill= "black", anchor = E)
    # points & lines
    for i in range(len(datarow.yValues)):
        x = mapValue(datarow.xValues[i], datarow.minX, datarow.maxX, xLeft, xRight)
        if np.isnan(datarow.yValues[i]):
            canvas.create_line(x, yUp, x, yDown, fill = "blue", width = 2)
        else:
            y = mapValue(datarow.yValues[i], datarow.minY, datarow.maxY, yDown, yUp)
            r = 3
            canvas.create_oval(x - r, y - r, x + r, y + r, fill = "black")

def loadData(title):
    path = filedialog.askopenfilename(title = title, filetypes = (("excel files", "*.xlsx"), ("csv files", "*.csv"), ("all files", "*.*")))
    file_extension = os.path.splitext(path)[1]
    if (file_extension == ".xlsx"):
        data = pd.read_excel(path, index_col = None, header = None)
    elif (file_extension == ".csv"):
        data = pd.read_csv(path, sep = ";", index_col = None, header = None)
    return data.to_numpy()

def mapValue(oldValue, oldMin, oldMax, newMin, newMax):
    oldRange = oldMax - oldMin
    newRange = newMax - newMin
    newValue = (oldValue - oldMin) * newRange / oldRange + newMin
    return newValue

def getExtremes(list):
    minValue = list[0]
    maxValue = list[0]
    for i in range(1, len(list)):
        value = list[i]
        if value < minValue:
            minValue = value
        elif value > maxValue:
            maxValue = value
    return minValue, maxValue

def setupDatarow(xValues):
    global datarow
    xValues = cleanValues(xValues)
    r = random.randrange(0, len(project.data["echte Messwerte"]))
    yValues = np.copy(project.data["echte Messwerte"][r]).astype(float)
    minX, maxX = getExtremes(xValues)
    minY, maxY = getExtremes(yValues)
    yRange = maxY - minY
    factor = random.uniform(0.2, 0.4)
    minY = minY - factor*yRange
    maxY = maxY + factor*yRange

    print(xValues)
    print(yValues)

    # for i in range(len(yValues)):
    #     if random.random() > 0.75:
    #         yValues[i] = np.nan
    r = random.randrange(0, len(yValues))
    yValues[r] = np.nan

    datarow = Datarow(xValues, yValues, minX, maxX, minY, maxY)

def cleanValues(values):
    for i in range(len(values)):
        v = values[i]
        if int(v) != v:
            return values
    return values.astype(np.int64)

def exportData(data, title):
    folder = filedialog.askdirectory()
    path = folder + "/" + title + ".xlsx"
    df = pd.DataFrame(data = data)
    df.to_excel(path, index = False, header = False)
    message = "Die Datei \""+ title + ".xlsx\" wurde erstellt."
    messagebox.showinfo(title = None, message = message)

# classes
class Project:
    def __init__(self, name, type, classNames, data):
        self.name = name
        self.type = type
        self.classNames = classNames
        self.data = data
        self.classifier = None
        self.accuracy = None

    def setup(self, name, type, classNames, data):
        self.name = name
        self.type = type
        self.classNames = classNames
        self.data = data
        if self.type == 2:
            self.classNames = ["echte Messwerte", "gefälschte Messwerte"]

    def addClass(self, className):
        self.classNames.append(className)

    def setData(self, data, key):
        self.data[key] = data

    def addData(self, data, key):
        if key in self.data and len(self.data[key]) > 0:
            self.data[key] = np.append(self.data[key], [data], axis = 0)
        else:
            self.data[key] = [data]

    def train(self):
        # check if all datasets have same length
        l = len(self.data[self.classNames[0]][0])
        for i in range(1, len(self.classNames)):
            className = self.classNames[i]
            l2 = len(self.data[self.classNames[i]][0])
            if l != l2:
                message = "Die Messwerte aus den Klassen \"" + self.classNames[0] + "\" und \"" + className + "\" haben nicht die gleiche Länge!"
                messagebox.showerror(title = None, message = message)
                return

        x = self.data[self.classNames[0]]
        for i in range(1, len(self.classNames)):
            className = self.classNames[i]
            x = np.concatenate((x, self.data[className]), axis = 0)

        yList = []
        for i in range(0, len(self.classNames)):
            className = self.classNames[i]
            for j in range(len(self.data[className])):
                yList.append(className)
        y = np.array(yList)

        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(x, y, test_size = 0.2, shuffle = True)

        self.classifier = svm.SVC(gamma = 0.001)
        self.classifier.fit(X_train, y_train)

        from sklearn.metrics import accuracy_score
        y_pred = self.classifier.predict(X_test)
        self.accuracy = accuracy_score(y_test, y_pred)

        self.classifier = svm.SVC(gamma = 0.001)
        self.classifier.fit(x, y)

    def test(self, data):
        pred = self.classifier.predict(data)
        top = Toplevel()
        # top.title("qwe")
        export_Data = np.hstack((data, np.reshape(pred, (len(pred), 1))))
        command = lambda: [exportData(export_Data, "überprüfte Messwerte")]
        Button(top, text = "export", command = command).grid(row = 0)
        for i in range(len(pred)):
            row = i + 100
            Label(top, text = i).grid(row = row, column = 0, sticky = E)
            Label(top, text = pred[i]).grid(row = row, column = 1, sticky = W)

    def trainable(self):
        for key in self.classNames:
            if key not in self.data:
                return False
            elif len(self.data[key]) == 0:
                return False
        return True

class Datarow:
    def __init__(self, xValues, yValues, minX, maxX, minY, maxY):
        self.xValues = xValues
        self.yValues = yValues
        self.minX = minX
        self.maxX = maxX
        self.minY = minY
        self.maxY = maxY
    def complete(self):
        array_sum = np.sum(self.yValues)
        array_has_nan = np.isnan(array_sum)
        return not array_has_nan

datarow = Datarow(np.empty(1), np.empty(1), 0, 1, 0, 1)
window = Tk()
project = Project("", 1, [], {})
createdFakeData = False
page_start()
# window.iconbitmap()
window.mainloop()
