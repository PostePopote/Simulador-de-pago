CREATE DATABASE `SakuraShop`;

USE `SakuraShop`;

CREATE TABLE `usuarios` (
  `id_usuario` int PRIMARY KEY AUTO_INCREMENT,
  `nombre` varchar(255),
  `gmail` varchar(255),
  `contraseña` varchar(255),
  `rol` varchar(255)
);
CREATE TABLE `productos` (
  `id_producto` int PRIMARY KEY AUTO_INCREMENT,
  `nombre` varchar(255),
  `precio` decimal,
  `stock` int,
  `tipo` varchar(255),
  `categoria` varchar(255)
);
CREATE TABLE `carrito` (
  `id_carrito` int PRIMARY KEY AUTO_INCREMENT,
  `id_usuario` int UNIQUE NOT NULL
);
CREATE TABLE `carrito_detalle` (
  `id_carrito_detalle` int PRIMARY KEY AUTO_INCREMENT,
  `id_carrito` int NOT NULL,
  `id_producto` int NOT NULL,
  `cantidad` int NOT NULL
);
CREATE TABLE `pedidos` (
  `id_pedido` int PRIMARY KEY AUTO_INCREMENT,
  `id_usuario` int NOT NULL,
  `fecha` datetime,
  `estado` varchar(255),
  `total` decimal
);
CREATE TABLE `pedido_detalle` (
  `id_pedido_detalle` int PRIMARY KEY AUTO_INCREMENT,
  `id_pedido` int NOT NULL,
  `id_producto` int NOT NULL,
  `cantidad` int NOT NULL,
  `precio_unitario` decimal NOT NULL
);
CREATE TABLE `pagos` (
  `id_pago` int PRIMARY KEY AUTO_INCREMENT,
  `id_pedido` int UNIQUE NOT NULL,
  `id_pago_mp` varchar(255),
  `metodo_pago` varchar(255),
  `estado` varchar(255),
  `monto` decimal,
  `fecha_pago` datetime
);

CREATE UNIQUE INDEX `carrito_detalle_index_0` ON `carrito_detalle` (`id_carrito`, `id_producto`);
ALTER TABLE `carrito` ADD FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`);
ALTER TABLE `carrito_detalle` ADD FOREIGN KEY (`id_carrito`) REFERENCES `carrito` (`id_carrito`);
ALTER TABLE `carrito_detalle` ADD FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`);
ALTER TABLE `pedidos` ADD FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`);
ALTER TABLE `pedido_detalle` ADD FOREIGN KEY (`id_pedido`) REFERENCES `pedidos` (`id_pedido`);
ALTER TABLE `pedido_detalle` ADD FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`);
ALTER TABLE `pagos` ADD FOREIGN KEY (`id_pedido`) REFERENCES `pedidos` (`id_pedido`);

ALTER TABLE productos
ADD COLUMN descripcion TEXT NULL;

ALTER TABLE productos
ADD COLUMN imagen VARCHAR(255) NULL;