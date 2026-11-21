from abc import ABC, abstractmethod
import logging
import re


# CONFIGURACIÓN DEL SISTEMA DE LOGS

logging.basicConfig(
    filename='software_fj.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    encoding='utf-8',
)



# EXCEPCIONES PERSONALIZADAS

class SoftwareFJError(Exception):
  """Excepción base para todos los errores del sistema Software FJ."""

  pass


class ClienteInvalidoError(SoftwareFJError):
  """Excepción lanzada cuando los datos del cliente no cumplen las reglas."""

  pass


class ServicioInvalidoError(SoftwareFJError):
  """Excepción lanzada ante fallos en la configuración o parámetros del servicio."""

  pass


class ReservaError(SoftwareFJError):
  """Excepción lanzada durante el flujo de creación o procesamiento de reservas."""

  pass


class ParametroInvalidoError(SoftwareFJError):
  """Excepción lanzada cuando un argumento u operación numérica es inválido."""

  pass



# CLASE ABSTRACTA BASE (Entidad General)

class EntidadBase(ABC):

  def __init__(self, id_entidad: str):
    if not id_entidad or not isinstance(id_entidad, str):
      raise ParametroInvalidoError(
          'El ID de la entidad debe ser una cadena de texto válida.'
      )
    self._id_entidad = id_entidad

  @property
  def id_entidad(self) -> str:
    return self._id_entidad

  @abstractmethod
  def obtener_detalles(self) -> str:
    """Método abstracto para retornar los detalles de la entidad."""
    pass



# CLASE CLIENTE (Encapsulación y Validaciones)

class Cliente(EntidadBase):

  def __init__(
      self, id_entidad: str, nombre: str, email: str, telefono: str
  ):
    super().__init__(id_entidad)
    self.nombre = nombre
    self.email = email
    self.telefono = telefono

  @property
  def nombre(self) -> str:
    return self._nombre

  @nombre.setter
  def nombre(self, valor: str):
    if not valor or len(valor.strip()) < 2:
      raise ClienteInvalidoError(
          'El nombre del cliente es obligatorio y debe tener al menos 2'
          ' caracteres.'
      )
    self._nombre = valor.strip()

  @property
  def email(self) -> str:
    return self._email

  @email.setter
  def email(self, valor: str):
    patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not valor or not re.match(patron, valor):
      raise ClienteInvalidoError(
          f'El correo electrónico "{valor}" tiene un formato inválido.'
      )
    self._email = valor

  @property
  def telefono(self) -> str:
    return self._telefono

  @telefono.setter
  def telefono(self, valor: str):
    if not valor or not valor.isdigit() or len(valor) < 7:
      raise ClienteInvalidoError(
          f'El teléfono "{valor}" debe contener únicamente dígitos y mínimo 7'
          ' caracteres.'
      )
    self._telefono = valor

  def obtener_detalles(self) -> str:
    return (
        f'Cliente [ID: {self.id_entidad} | Nombre: {self.nombre} | Email:'
        f' {self.email} | Teléfono: {self.telefono}]'
    )



# CLASE ABSTRACTA SERVICIO (Polimorfismo)

class Servicio(EntidadBase):

  def __init__(self, id_entidad: str, nombre_servicio: str, tarifa_base: float):
    super().__init__(id_entidad)
    self.nombre_servicio = nombre_servicio
    self.tarifa_base = tarifa_base

  @property
  def tarifa_base(self) -> float:
    return self._tarifa_base

  @tarifa_base.setter
  def tarifa_base(self, valor: float):
    if valor <= 0:
      raise ServicioInvalidoError(
          'La tarifa base del servicio debe ser mayor estrictamente a cero.'
      )
    self._tarifa_base = float(valor)

  @abstractmethod
  def calcular_costo(self, duracion: float, **kwargs) -> float:
    """Calcula el costo del servicio aplicando reglas específicas."""
    pass

  @abstractmethod
  def obtener_descripcion(self) -> str:
    """Retorna la descripción detallada del servicio."""
    pass

  @abstractmethod
  def validar_parametros(self, **kwargs) -> bool:
    """Valida los parámetros específicos de operación del servicio."""
    pass

  def obtener_detalles(self) -> str:
    return self.obtener_descripcion()



# SERVICIO 1: Reserva de Salas

class ReservaSala(Servicio):

  def __init__(
      self,
      id_entidad: str,
      nombre_servicio: str,
      tarifa_base: float,
      capacidad: int,
  ):
    super().__init__(id_entidad, nombre_servicio, tarifa_base)
    self.capacidad = capacidad

  @property
  def capacidad(self) -> int:
    return self._capacidad

  @capacidad.setter
  def capacidad(self, valor: int):
    if valor <= 0:
      raise ServicioInvalidoError(
          'La capacidad de la sala debe ser mayor a cero.'
      )
    self._capacidad = int(valor)

  def validar_parametros(self, **kwargs) -> bool:
    personas = kwargs.get('personas', 1)
    if personas > self.capacidad:
      raise ServicioInvalidoError(
          f'La cantidad de asistentes ({personas}) supera la capacidad máxima'
          f' de la sala ({self.capacidad}).'
      )
    return True

  # Método con parámetros opcionales para simular sobrecarga de cálculos
  def calcular_costo(
      self, duracion: float, descuento: float = 0.0, impuesto: float = 0.19
  ) -> float:
    if duracion <= 0:
      raise ParametroInvalidoError(
          'La duración en horas debe ser mayor a cero.'
      )
    subtotal = self.tarifa_base * duracion
    subtotal_con_desc = subtotal * (1 - descuento)
    total = subtotal_con_desc * (1 + impuesto)
    return round(total, 2)

  def obtener_descripcion(self) -> str:
    return (
        f'Reserva de Sala: {self.nombre_servicio} [Capacidad: {self.capacidad}'
        f' personas] - Tarifa/hora: ${self.tarifa_base}'
    )



# SERVICIO 2: Alquiler de Equipos

class AlquilerEquipo(Servicio):

  def __init__(
      self,
      id_entidad: str,
      nombre_servicio: str,
      tarifa_base: float,
      deposito: float,
  ):
    super().__init__(id_entidad, nombre_servicio, tarifa_base)
    self.deposito = deposito

  @property
  def deposito(self) -> float:
    return self._deposito

  @deposito.setter
  def deposito(self, valor: float):
    if valor < 0:
      raise ServicioInvalidoError(
          'El valor del depósito garantía no puede ser negativo.'
      )
    self._deposito = float(valor)

  def validar_parametros(self, **kwargs) -> bool:
    return True  # Sin restricciones adicionales de parámetros

  def calcular_costo(
      self,
      dias: float,
      incluir_deposito: bool = True,
      descuento: float = 0.0,
  ) -> float:
    if dias <= 0:
      raise ParametroInvalidoError(
          'Los días de alquiler deben ser mayores a cero.'
      )
    subtotal = self.tarifa_base * dias
    total_desc = subtotal * (1 - descuento)
    total = total_desc + (self.deposito if incluir_deposito else 0.0)
    return round(total, 2)

  def obtener_descripcion(self) -> str:
    return (
        f'Alquiler de Equipo: {self.nombre_servicio} - Tarifa/día:'
        f' ${self.tarifa_base} (Depósito: ${self.deposito})'
    )



# SERVICIO 3: Asesorías Especializadas

class AsesoriaEspecializada(Servicio):

  def __init__(
      self,
      id_entidad: str,
      nombre_servicio: str,
      tarifa_base: float,
      nivel_experto: str,
  ):
    super().__init__(id_entidad, nombre_servicio, tarifa_base)
    self.nivel_experto = nivel_experto

  @property
  def nivel_experto(self) -> str:
    return self._nivel_experto

  @nivel_experto.setter
  def nivel_experto(self, valor: str):
    niveles_permitidos = ['Junior', 'Senior', 'Master']
    if valor not in niveles_permitidos:
      raise ServicioInvalidoError(
          f'Nivel experto inválido. Opciones permitidas: {niveles_permitidos}'
      )
    self._nivel_experto = valor

  def validar_parametros(self, **kwargs) -> bool:
    horas = kwargs.get('duracion', 1)
    if self.nivel_experto == 'Master' and horas < 2:
      raise ServicioInvalidoError(
          'Las asesorías de nivel Master requieren una contratación mínima de'
          ' 2 horas.'
      )
    return True

  def calcular_costo(
      self,
      horas: float,
      factor_urgencia: float = 1.0,
      impuesto: float = 0.19,
  ) -> float:
    if horas <= 0:
      raise ParametroInvalidoError(
          'Las horas de asesoría deben ser mayores a cero.'
      )
    subtotal = self.tarifa_base * horas * factor_urgencia
    total = subtotal * (1 + impuesto)
    return round(total, 2)

  def obtener_descripcion(self) -> str:
    return (
        f'Asesoría Especializada: {self.nombre_servicio} [Nivel:'
        f' {self.nivel_experto}] - Tarifa/hora: ${self.tarifa_base}'
    )



# CLASE RESERVA (Gestión integral con excepciones avanzadas)

class Reserva(EntidadBase):

  def __init__(
      self,
      id_entidad: str,
      cliente: Cliente,
      servicio: Servicio,
      duracion: float,
      **kwargs,
  ):
    super().__init__(id_entidad)
    self.cliente = cliente
    self.servicio = servicio
    self.duracion = duracion
    self.parametros_extra = kwargs
    self.estado = 'Pendiente'
    self.costo_total = 0.0

  @property
  def duracion(self) -> float:
    return self._duracion

  @duracion.setter
  def duracion(self, valor: float):
    if valor <= 0:
      raise ReservaError('La duración de la reserva debe ser mayor a cero.')
    self._duracion = float(valor)

  def procesar_reserva(self):
    """Procesa la reserva utilizando try/except/else/finally y encadenamiento de excepciones."""
    logging.info(
        f'Iniciando procesamiento de la reserva ID: {self.id_entidad}'
    )
    try:
      # Validaciones y cálculos polimórficos
      self.servicio.validar_parametros(
          duracion=self.duracion, **self.parametros_extra
      )
      self.costo_total = self.servicio.calcular_costo(
          self.duracion, **self.parametros_extra
      )

    except (ServicioInvalidoError, ParametroInvalidoError) as e:
      self.estado = 'Fallida'
      logging.error(
          f'Error operativo al procesar reserva {self.id_entidad}: {e}'
      )
      # Encadenamiento de excepciones con 'raise ... from ...'
      raise ReservaError(
          f'No fue posible procesar la reserva {self.id_entidad} debido a un'
          ' error en los parámetros.'
      ) from e

    except Exception as e:
      self.estado = 'Fallida'
      logging.critical(
          f'Error crítico inesperado en reserva {self.id_entidad}: {e}'
      )
      raise ReservaError(
          f'Fallo crítico general en la reserva {self.id_entidad}.'
      ) from e

    else:
      self.estado = 'Confirmada'
      logging.info(
          f'Reserva {self.id_entidad} confirmada exitosamente. Costo calculado:'
          f' ${self.costo_total}'
      )

    finally:
      logging.info(
          f'Finalizado ciclo de procesamiento para reserva {self.id_entidad}.'
          f' Estado final: {self.estado}'
      )

  def cancelar(self):
    if self.estado == 'Cancelada':
      logging.warning(
          f'Intento de cancelar una reserva ya cancelada ({self.id_entidad}).'
      )
      return
    self.estado = 'Cancelada'
    logging.info(f'Reserva {self.id_entidad} cancelada correctamente.')

  def obtener_detalles(self) -> str:
    return (
        f'Reserva [ID: {self.id_entidad} | Cliente: {self.cliente.nombre} |'
        f' Servicio: {self.servicio.nombre_servicio} | Estado: {self.estado} |'
        f' Costo: ${self.costo_total}]'
    )



# SIMULACIÓN DE 10 OPERACIONES (Software FJ)

if __name__ == '__main__':
  print('==================================================')
  print(' INICIANDO SIMULACIÓN DE OPERACIONES - SOFTWARE FJ')
  print('==================================================\n')

  lista_clientes = []
  lista_servicios = []
  lista_reservas = []

  # Operación 1: Registro correcto de un cliente
  print('--- Operando 1: Registro Válido de Cliente ---')
  try:
    c1 = Cliente('C001', 'Carlos Mendoza', 'carlos.mendoza@email.com', '3001234567')
    lista_clientes.append(c1)
    print(f'[ÉXITO] {c1.obtener_detalles()}')
  except Exception as e:
    print(f'[ERROR] {e}')

  # Operación 2: Registro inválido de un cliente (Correo incorrecto)
  print('\n--- Operando 2: Registro Inválido de Cliente (Excepción) ---')
  try:
    c2 = Cliente(
        'C002', 'Ana Gómez', 'correo-invalido-sin-arroba', '3119876543'
    )
    lista_clientes.append(c2)
  except SoftwareFJError as e:
    print(
        '[CONTROLADO] Excepción capturada correctamente al registrar'
        f' cliente:\n  -> {e}'
    )

  # Operación 3: Creación correcta de un servicio (Reserva de Sala)
  print('\n--- Operando 3: Creación Correcta de Servicio (Sala) ---')
  try:
    s1 = ReservaSala('S001', 'Sala Ejecutiva Alpha', 50.0, capacidad=10)
    lista_servicios.append(s1)
    print(f'[ÉXITO] {s1.obtener_detalles()}')
  except Exception as e:
    print(f'[ERROR] {e}')

  # Operación 4: Creación incorrecta de un servicio (Tarifa base negativa)
  print('\n--- Operando 4: Creación Inválida de Servicio (Excepción) ---')
  try:
    s_err = AlquilerEquipo('S002', 'Servidor Rack', -120.0, deposito=200.0)
    lista_servicios.append(s_err)
  except SoftwareFJError as e:
    print(
        '[CONTROLADO] Excepción capturada al intentar crear servicio con'
        f' tarifa inválida:\n  -> {e}'
    )

  # Operación 5: Creación correcta de Alquiler de Equipo y Asesoría
  print(
      '\n--- Operando 5 y 6: Creación de Alquiler de Equipo y Asesoría ---'
  )
  try:
    s2 = AlquilerEquipo('S003', 'Kit Audiovisual Pro', 80.0, deposito=150.0)
    s3 = AsesoriaEspecializada(
        'S004', 'Arquitectura Cloud', 120.0, nivel_experto='Master'
    )
    lista_servicios.extend([s2, s3])
    print(f'[ÉXITO] {s2.obtener_detalles()}')
    print(f'[ÉXITO] {s3.obtener_detalles()}')
  except Exception as e:
    print(f'[ERROR] {e}')

  # Operación 7: Procesamiento de Reserva Exitosa (Sala)
  print('\n--- Operando 7: Reserva Exitosa de Sala ---')
  try:
    r1 = Reserva('R001', c1, s1, duracion=3.0, personas=5, descuento=0.1)
    r1.procesar_reserva()
    lista_reservas.append(r1)
    print(f'[ÉXITO] {r1.obtener_detalles()}')
  except Exception as e:
    print(f'[ERROR] {e}')

  # Operación 8: Procesamiento de Reserva Fallida por superación de capacidad
  print(
      '\n--- Operando 8: Reserva Fallida (Capacidad Superada - Excepción) ---'
  )
  try:
    r2 = Reserva(
        'R002', c1, s1, duracion=2.0, personas=15
    )  # Capacidad máxima es 10
    r2.procesar_reserva()
  except ReservaError as e:
    print(
        '[CONTROLADO] Excepción de reserva capturada de forma segura:\n  ->'
        f' {e}'
    )

  # Operación 9: Procesamiento de Reserva Exitosa (Asesoría Master con horas suficientes)
  print('\n--- Operando 9: Reserva Exitosa de Asesoría Especializada ---')
  try:
    c3 = Cliente(
        'C003', 'Lucía Pérez', 'lucia.perez@softwarefj.com', '3204567890'
    )
    r3 = Reserva(
        'R003', c3, s3, duracion=3.0, factor_urgencia=1.2
    )  # Master con 3 horas (cumple mínimo 2)
    r3.procesar_reserva()
    lista_reservas.append(r3)
    print(f'[ÉXITO] {r3.obtener_detalles()}')
  except Exception as e:
    print(f'[ERROR] {e}')

  # Operación 10: Cancelación de una reserva confirmada
  print('\n--- Operando 10: Cancelación de Reserva Existente ---')
  try:
    print(f'Estado previo: {r1.estado}')
    r1.cancelar()
    print(f'[ÉXITO] Estado posterior tras cancelación: {r1.estado}')
  except Exception as e:
    print(f'[ERROR] {e}')

  print('\n==================================================')
  print(
      ' SIMULACIÓN FINALIZADA CON ÉXITO. REVISAR ARCHIVO "software_fj.log".'
  )
  print('==================================================')