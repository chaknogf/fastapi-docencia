from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.exc import SQLAlchemyError
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import os
import tempfile
from pathlib import Path
import time

from app.database.db import SessionLocal
from app.models.actividades import VistaActividad
from app.schemas.actividad import ActividadVista
from fastapi.security import OAuth2PasswordBearer

# =========================
# ROUTER Y SEGURIDAD
# =========================
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# =========================
# DEPENDENCIA DE DB
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 


# =========================
# FUNCIÓN AUXILIAR: LIMPIAR ARCHIVOS ANTIGUOS
# =========================
def limpiar_reportes_antiguos(directorio: Path, horas: int = 24):
    """
    Elimina archivos de reporte más antiguos que el número de horas especificado.
    """
    try:
        ahora = time.time()
        limite = ahora - (horas * 3600)
        
        for archivo in directorio.glob("reporte_actividades_*.xlsx"):
            if archivo.stat().st_mtime < limite:
                archivo.unlink()
    except Exception:
        pass  # Ignorar errores de limpieza


# =========================
# ENDPOINT: GENERAR REPORTE EXCEL
# =========================
@router.get("/reporte/excel", tags=["reportes"])
async def generar_reporte_excel(
    anio: Optional[int] = Query(None),
    # token: str = Depends(oauth2_scheme),
    db: SQLAlchemySession = Depends(get_db)
):
    """
    Genera un reporte en Excel de las actividades con filtros opcionales.
    Retorna el archivo Excel para descarga.
    """
    try:
        # Construir query con filtros
        query = db.query(VistaActividad)
        
        if anio:
            query = query.filter(VistaActividad.anio == anio)

        # Ordenar por fecha
        actividades = query.order_by(VistaActividad.fecha_programada).all()

        if not actividades:
            raise HTTPException(status_code=404, detail="No se encontraron actividades con los filtros especificados")

        # Crear directorio temporal si no existe
        temp_dir = Path(tempfile.gettempdir()) / "reportes_excel"
        temp_dir.mkdir(exist_ok=True)

        # Limpiar archivos antiguos (más de 24 horas)
        limpiar_reportes_antiguos(temp_dir, horas=24)

        # Crear archivo Excel
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Reporte de Actividades"

        # Estilos
        header_font = Font(bold=True, color="FFFFFF", size=12)
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

        # Encabezados
        headers = [
            "ID", "Tema", "Actividad", "Servicio", "Responsable", 
            "Fecha Programada", "Modalidad", "Estado", "Mes", "Año",
            "Fecha Entrega Informe", "Observaciones"
        ]
        
        ws.append(headers)

        # Aplicar estilo a encabezados
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
            cell.border = border

        # Agregar datos
        for act in actividades:
            # Extraer responsable del JSON
            responsable = ""
            if act.persona_responsable and 'r0' in act.persona_responsable:
                responsable = act.persona_responsable['r0'].get('nombre', '')

            # Extraer fecha de entrega del JSON de detalles
            fecha_entrega = ""
            observaciones = ""
            if act.detalles:
                fecha_entrega = act.detalles.get('fecha_entrega_informe', '')
                observaciones = act.detalles.get('observaciones', '')

            row_data = [
                act.id,
                act.tema,
                act.actividad,
                act.servicio_encargado,
                responsable,
                act.fecha_programada.strftime('%Y-%m-%d') if act.fecha_programada else '',
                act.modalidad,
                act.estado,
                act.mes_id,
                act.anio,
                fecha_entrega,
                observaciones
            ]
            
            ws.append(row_data)

        # Ajustar ancho de columnas
        column_widths = {
            'A': 8,   # ID
            'B': 30,  # Tema
            'C': 40,  # Actividad
            'D': 15,  # Servicio
            'E': 25,  # Responsable
            'F': 18,  # Fecha Programada
            'G': 15,  # Modalidad
            'H': 15,  # Estado
            'I': 8,   # Mes
            'J': 8,   # Año
            'K': 20,  # Fecha Entrega
            'L': 30   # Observaciones
        }

        for col, width in column_widths.items():
            ws.column_dimensions[col].width = width

        # Aplicar bordes a todas las celdas con datos
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=1, max_col=len(headers)):
            for cell in row:
                cell.border = border
                cell.alignment = Alignment(vertical="top", wrap_text=True)

        # Congelar primera fila
        ws.freeze_panes = "A2"

        # Agregar filtros
        ws.auto_filter.ref = ws.dimensions

        # Nombre del archivo con timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"reporte_actividades_{timestamp}.xlsx"
        filepath = temp_dir / filename

        # Guardar archivo
        wb.save(str(filepath))

        # Retornar archivo para descarga
        return FileResponse(
            path=str(filepath),
            filename=filename,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar reporte: {str(e)}")