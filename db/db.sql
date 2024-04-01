CREATE TABLE Registros (
  N_Atencion INT NOT NULL AUTO_INCREMENT,
  CNE INT NOT NULL,
  Comuna INT NOT NULL,
  Manzana INT NOT NULL,
  Predio INT NOT NULL,
  Enajenantes TEXT NOT NULL,
  Adquirentes TEXT NOT NULL,
  Fojas INT NOT NULL,
  Fecha_Inscripcion DATE NOT NULL,
  Numero_Inscripcion INT NOT NULL,
  PRIMARY KEY (N_Atencion)
);

ALTER TABLE Registros ADD INDEX idx_registro_clave (Comuna, Manzana, Predio);


CREATE TABLE Multipropietarios (
  Comuna INT NOT NULL,
  Manzana INT NOT NULL,
  Predio INT NOT NULL,
  RUN_RUT VARCHAR(12) NOT NULL,
  Porcentaje_Derechos INT,
  Fojas INT NOT NULL,
  Ano_Inscripcion INT,
  Numero_Inscripcion INT NOT NULL,
  Fecha_Inscripcion DATE NOT NULL,
  Ano_Vigencia_Inicial INT,
  Ano_Vigencia_Final INT,
  PRIMARY KEY (Comuna, Manzana, Predio, RUN_RUT, Numero_Inscripcion)
);
ALTER TABLE Multipropietarios
  ADD FOREIGN KEY (Comuna, Manzana, Predio)
  REFERENCES Registros (Comuna, Manzana, Predio);