import cv2.cv as cv
from datetime import datetime
import time

class KaptisCodigo():
    
    def cambioUsuarioValores(self, val):
        self.threshold = val
    
    #Constructor de clase
    def __init__(self,threshold=5, camara=0, mostrarVentana=True):
        
        self.writer = None
        self.font = None
        self.show = mostrarVentana
        self.frame = None
    
        #Tomamos una captura inicial
        self.capture=cv.CaptureFromCAM(camara) #La camara puede ubicarse en otro numero 0, 1, 2...
        self.frame = cv.QueryFrame(self.capture) 
        
        #Inicializamos variables
        self.gray_frame = cv.CreateImage(cv.GetSize(self.frame), cv.IPL_DEPTH_8U, 1)
        self.average_frame = cv.CreateImage(cv.GetSize(self.frame), cv.IPL_DEPTH_32F, 3)
        self.absdiff_frame = None
        self.previous_frame = None
        
        self.surface = self.frame.width * self.frame.height
        self.currentsurface = 0
        self.currentcontours = None
        self.threshold = threshold
        self.isRecording = True
        self.trigger_time = 0 
        
        if mostrarVentana:
            cv.NamedWindow("Imagen")
            cv.CreateTrackbar("Valor threshold: ", "Imagen", self.threshold, 100, self.cambioUsuarioValores)
        
    #Inicializador de grabacion
    def iniciarGrabacion(self):
        codec = cv.CV_FOURCC('D', 'I', 'V', 'X') #Codificacion
        self.writer=cv.CreateVideoWriter("grabaciones/Grabacion-"+datetime.now().strftime("%b-%d_%H_%M_%S")+".avi", codec, 4, cv.GetSize(self.frame), 1)
        self.font = cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX, 1, 1, 0, 2, 8) #Fuente para el mensaje a imprimir en el video

    #Metodo de ejecucion continua
    def ejecucion(self):
        started = time.time()
        while True:
            #Tomamos una instantanea de la camara
            currentframe = cv.QueryFrame(self.capture)
            #Obtenemos el timestamp actual para grabar en la imagen
            instant = time.time() 
            
            #Procesamos la imagen
            self.procesarImagen(currentframe) 
            
            if not self.isRecording:
                if self.algoSeMueve():
                    self.trigger_time = instant 
                    if instant > started +10:
                        print "Movimiento detectado! Grabando"
                        self.isRecording = True
                cv.DrawContours (currentframe, self.currentcontours, (0, 0, 1000), (0, 1000, 0), 1, 2, cv.CV_FILLED)
            else:
                if instant >= self.trigger_time +10: 
                    print "Grabacion detenida"
                    self.isRecording = False
                else:
                    #Seteamos la fecha en la imagen actual
                    cv.PutText(currentframe,datetime.now().strftime("%b %d, %H:%M:%S"), (25,30),self.font, 0) 
                    #Grabamos la imagen en el video
                    cv.WriteFrame(self.writer, currentframe) 
            
            if self.show:
                cv.ShowImage("Imagen", currentframe)
                
            #Detenemos la grabacion si el usuario presiona ESC
            c=cv.WaitKey(1) % 0x100
            if c==27 or c == 10: 
                break            
    
    #Compara las imagenes para detectar movimiento
    def procesarImagen(self, curframe):
        #Rebajamos los falsos positivos con un filtro Smooth
        cv.Smooth(curframe, curframe) 
        
        #Contemplamos el caso de la primera ejecucion de este metodo
        if not self.absdiff_frame: 
            self.absdiff_frame = cv.CloneImage(curframe)
            self.previous_frame = cv.CloneImage(curframe)
            cv.Convert(curframe, self.average_frame) 
        else:
        #En caso contrario se calcula la media
            cv.RunningAvg(curframe, self.average_frame, 0.05) 
        
        cv.Convert(self.average_frame, self.previous_frame) 
        
        cv.AbsDiff(curframe, self.previous_frame, self.absdiff_frame) 
        
        cv.CvtColor(self.absdiff_frame, self.gray_frame, cv.CV_RGB2GRAY) 
        cv.Threshold(self.gray_frame, self.gray_frame, 50, 255, cv.CV_THRESH_BINARY)

        cv.Dilate(self.gray_frame, self.gray_frame, None, 15) 
        cv.Erode(self.gray_frame, self.gray_frame, None, 10)

            
    def algoSeMueve(self):
        # Buscamos contornos
        storage = cv.CreateMemStorage(0)
        contours = cv.FindContours(self.gray_frame, storage, cv.CV_RETR_EXTERNAL, cv.CV_CHAIN_APPROX_SIMPLE)

        self.currentcontours = contours #Guardamos los contornos
        
        while contours: #Sumamos el area de cada contorno
            self.currentsurface += cv.ContourArea(contours)
            contours = contours.h_next()
        
        avg = (self.currentsurface*100)/self.surface #Calculamos la media del contorno detectado con respecto a la imagen
        self.currentsurface = 0 
        
        if avg > self.threshold:
            return True
        else:
            return False

        
if __name__=="__main__":
    detect = KaptisCodigo()
    detect.ejecucion()

