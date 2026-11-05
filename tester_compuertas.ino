onst int entradasA[] = {1, 4, 8, 11};  
const int entradasB[] = {2, 5, 9, 12};  
const int salidasY[]  = {3, 6, 7, 10};  

void setup() {
  Serial.begin(115200);
  
  while (!Serial) {
    delay(10); 
  }
}

void loop() {
  if (Serial.available() > 0) {
    char tipoIC = Serial.read();
    
    if(tipoIC == 'A' || tipoIC == 'O') {
      probarIC_CuatroCompuertas(tipoIC);
    } 
    else if(tipoIC == 'N') {
      probarIC_SeisCompuertasNOT();
    }
  }
}

void probarIC_CuatroCompuertas(char tipo) {
  for(int i = 0; i < 4; i++) {
    pinMode(entradasA[i], OUTPUT);
    pinMode(entradasB[i], OUTPUT);
    pinMode(salidasY[i], INPUT);
  }

  String resultados = "";
  bool integradoFunciona = true;

  for (int c = 0; c < 4; c++) {
    bool compuertaOK = true;

    for (int a = 0; a <= 1; a++) {
      for (int b = 0; b <= 1; b++) {
        digitalWrite(entradasA[c], a);
        digitalWrite(entradasB[c], b);
        delayMicroseconds(50); 
        
        int leido = digitalRead(salidasY[c]);
        int esperado = 0;

        if (tipo == 'A') esperado = a & b;
        else if (tipo == 'O') esperado = a | b;

        if (leido != esperado) {
          compuertaOK = false;
        }
      }
    }
    
    if(!compuertaOK) {
      integradoFunciona = false;
    }
    resultados += "C" + String(c+1) + ":" + String(compuertaOK ? "OK" : "FAIL") + ",";
  }

  Serial.println("STATUS:" + String(integradoFunciona ? "GOOD" : "BAD") + "," + resultados);
}

void probarIC_SeisCompuertasNOT() {
  int entradasNOT[] = {1, 3, 5, 9, 11, 13};
  int salidasNOT[]  = {2, 4, 6, 8, 10, 12};

  for(int i = 0; i < 6; i++) {
    pinMode(entradasNOT[i], OUTPUT);
    pinMode(salidasNOT[i], INPUT);
  }

  String resultados = "";
  bool integradoFunciona = true;

  for (int c = 0; c < 6; c++) {
    bool compuertaOK = true;

    for (int entrada = 0; entrada <= 1; entrada++) {
      digitalWrite(entradasNOT[c], entrada);
      delayMicroseconds(50);

      int leido = digitalRead(salidasNOT[c]);
      int esperado = !entrada;

      if (leido != esperado) {
        compuertaOK = false;
      }
    }

    if(!compuertaOK) {
      integradoFunciona = false;
    }
    resultados += "C" + String(c+1) + ":" + String(compuertaOK ? "OK" : "FAIL") + ",";
  }
  Serial.println("STATUS:" + String(integradoFunciona ? "GOOD" : "BAD") + "," + resultados);
}
