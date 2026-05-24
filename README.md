# Dockerized Honeypot - Infraestructura de Seguridad

Este proyecto implementa un Honeypot contenerizado utilizando Docker. Está diseñado para actuar como un señuelo dentro de una red, permitiendo el monitoreo pasivo del tráfico, el registro de intentos de acceso no autorizados y el análisis de vectores de ataque de manera segura y aislada.

## Enfoque y Arquitectura (Blue Team)

La arquitectura se basa en el principio de aislamiento de servicios. Al desplegar el honeypot dentro de contenedores, se garantiza que cualquier actividad maliciosa quede encapsulada, protegiendo el host principal (desplegado originalmente sobre entornos Linux) y permitiendo una recolección de métricas limpia y fácil de auditar.

## Características Principales

- **Aislamiento de Entorno:** Uso de contenedores Docker para encapsular el entorno vulnerable simulado, previniendo escaladas de privilegios al sistema host.
- **Monitoreo de Tráfico:** Captura y registro de intentos de conexión y comandos ejecutados por posibles atacantes.
- **Despliegue Rápido y Escalable:** Configuración lista para levantarse en cuestión de segundos en cualquier servidor que cuente con el motor de Docker.

## Tecnologías Utilizadas

- **Infraestructura:** Docker / Docker Compose.
- **Sistemas Operativos:** Optimizado para despliegues en distribuciones Linux.
- **Redes:** Aislamiento de red mediante redes virtuales de Docker (Bridge/Overlay).

## Despliegue Rápido

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/jk724pkj8w-stack/Honeypot.git](https://github.com/jk724pkj8w-stack/Honeypot.git)
   cd Honeypot
2. **Construir y levantar el contenedor:**
   (Asegúrate de tener el demonio de Docker corriendo)
   docker compose up -d --build
   O alternativamente mediante el comando run tradicional si no usas compose:
   docker run -d -p [puerto_expuesto]:[puerto_interno] honeypot-image
**Proyecto desarrollado con un enfoque en ciberseguridad defensiva y auditoría de sistemas.**
