const int entradasA[] = {1, 4, 8, 11};
const int entradasB[] = {2, 5, 9, 12};
const int salidasY[]  = {3, 6, 7, 10};

const int entradasNOT[] = {1, 3, 5, 9, 11, 13};
const int salidasNOT[]  = {2, 4, 6, 8, 10, 12};

void imprimirPrueba(
  const char* tipo,
  int compuerta,
  int entradaA,
  int entradaB,
  bool tieneEntradaB,
  int esperado,
  int medido
) {
  Serial.print("TEST,");
  Serial.print(tipo);
  Serial.print(",");
  Serial.print(compuerta);
  Serial.print(",");
  Serial.print(entradaA);
  Serial.print(",");

  if (tieneEntradaB) {
    Serial.print(entradaB);
  } else {
    Serial.print("-");
  }

  Serial.print(",");
  Serial.print(esperado);
  Serial.print(",");
  Serial.println(medido);
}

void configurarPinesCuatroCompuertas() {
  for (int i = 0; i < 4; i++) {
    pinMode(entradasA[i], OUTPUT);
    pinMode(entradasB[i], OUTPUT);
    pinMode(salidasY[i], INPUT);
  }
}

void configurarPinesSeisCompuertasNOT() {
  for (int i = 0; i < 6; i++) {
    pinMode(entradasNOT[i], OUTPUT);
    pinMode(salidasNOT[i], INPUT);
  }
}

void probarICCuatroCompuertas(char tipo) {
  configurarPinesCuatroCompuertas();

  const char* nombreTipo = (tipo == 'A') ? "AND" : "OR";
  bool integradoFunciona = true;

  for (int c = 0; c < 4; c++) {
    bool compuertaOK = true;

    for (int a = 0; a <= 1; a++) {
      for (int b = 0; b <= 1; b++) {
        digitalWrite(entradasA[c], a);
        digitalWrite(entradasB[c], b);

        delayMicroseconds(100);

        const int medido = digitalRead(salidasY[c]);
        const int esperado = (tipo == 'A') ? (a & b) : (a | b);

        imprimirPrueba(
          nombreTipo,
          c + 1,
          a,
          b,
          true,
          esperado,
          medido
        );

        if (medido != esperado) {
          compuertaOK = false;
        }
      }
    }

    if (!compuertaOK) {
      integradoFunciona = false;
    }
  }

  Serial.print("DONE,");
  Serial.print(nombreTipo);
  Serial.print(",");
  Serial.println(integradoFunciona ? "GOOD" : "BAD");
}

void probarICSeisCompuertasNOT() {
  configurarPinesSeisCompuertasNOT();

  bool integradoFunciona = true;

  for (int c = 0; c < 6; c++) {
    bool compuertaOK = true;

    for (int entrada = 0; entrada <= 1; entrada++) {
      digitalWrite(entradasNOT[c], entrada);

      delayMicroseconds(100);

      const int medido = digitalRead(salidasNOT[c]);
      const int esperado = !entrada;

      imprimirPrueba(
        "NOT",
        c + 1,
        entrada,
        0,       
        false,
        esperado,
        medido
      );

      if (medido != esperado) {
        compuertaOK = false;
      }
    }

    if (!compuertaOK) {
      integradoFunciona = false;
    }
  }

  Serial.print("DONE,NOT,");
  Serial.println(integradoFunciona ? "GOOD" : "BAD");
}

void setup() {
  Serial.begin(115200);


}

void loop() {
  if (Serial.available() <= 0) {
    return;
  }

  const char tipoIC = Serial.read();

  if (tipoIC == '\n' || tipoIC == '\r' || tipoIC == ' ') {
    return;
  }

  if (tipoIC == 'A' || tipoIC == 'O') {
    probarICCuatroCompuertas(tipoIC);
  } else if (tipoIC == 'N') {
    probarICSeisCompuertasNOT();
  } else {
    Serial.println("ERROR,COMANDO_NO_VALIDO");
  }
}
