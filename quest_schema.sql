-- noinspection SqlNoDataSourceInspectionForFile

CREATE TABLE IF NOT EXISTS phase (
  ts timestamp,
  phase symbol,
  voltage float,
  current float,
  power_active float,
  power_reactive float,
  power_apparent float
);

CREATE TABLE IF NOT EXISTS electric_avg (
  ts timestamp,
  current_demand float,
  power_active_demand float,
  power_apparent_demand float
);

CREATE TABLE IF NOT EXISTS panel (
  ts timestamp,
  pressure_status boolean, /* Napięcie */
  diverter_status boolean, /* Odchylacze */
  oil_status boolean, /* olej */
  water_status boolean, /* woda */
  water_level int, /* przyjmuje wartości 1, 2, 3, jak LEDy na panelu */
  diverter_position int /* przyjmuje wartości 1, 2, 3, 4 */
);

