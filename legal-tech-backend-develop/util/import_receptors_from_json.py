import json
from uuid import UUID
from sqlalchemy import create_engine
from sqlmodel import Session, select

from config import Config
from models.sql.receptor import Receptor, ReceptorDetail
from models.sql.tribunal import Tribunal

# ========================
# CONFIGURACIÓN DE CONEXIÓN
# ========================
engine = create_engine(Config.DATABASE_URL, echo=False)

# ========================
# LECTURA DEL JSON
# ========================
json_path = "" # add path here
print(f"📂 Leyendo archivo: {json_path}")
with open(json_path, "r", encoding="utf-8") as file:
    receptores = json.load(file)

print(f"📊 Total de receptores en JSON: {len(receptores)}")

# ========================
# INSERCIÓN DE DATOS
# ========================
insertados = 0
omitidos = 0
detalles_insertados = 0
tribunales_no_encontrados = set()

with Session(engine) as session:
    for idx, r in enumerate(receptores, 1):
        recepthor_external_id = r.get("recepthorId")
        
        if not recepthor_external_id:
            print(f"⚠️  Receptor sin ID externo, omitido: {r.get('name')}")
            omitidos += 1
            continue

        try:
            recepthor_external_id_uuid = UUID(recepthor_external_id)
        except ValueError:
            print(f"⚠️  ID externo inválido, omitido: {recepthor_external_id}")
            omitidos += 1
            continue

        # Verificar si ya existe
        existing = session.exec(
            select(Receptor).where(Receptor.recepthor_external_id == recepthor_external_id_uuid)
        ).first()

        if existing:
            print(f"⚠️  [{idx}/{len(receptores)}] Receptor ya existe, omitido: {r.get('name')}")
            omitidos += 1
            continue

        # Crear nuevo Receptor
        receptor = Receptor(
            recepthor_external_id=recepthor_external_id_uuid,
            name=r.get("name"),
            primary_email=r.get("primaryEmail"),
            secondary_email=r.get("secondaryEmail"),
            primary_phone=r.get("primaryPhone"),
            secondary_phone=r.get("secondaryPhone"),
            address=r.get("address")
        )
        
        session.add(receptor)
        session.flush()  # Para obtener el ID generado
        
        # Insertar los tribunales (profiles)
        profiles = r.get("profiles", [])
        for p in profiles:
            tribunal_id_str = p.get("tribunalId")
            
            if not tribunal_id_str:
                continue
            
            try:
                tribunal_id_uuid = UUID(tribunal_id_str)
            except ValueError:
                print(f"  ⚠️  Tribunal ID inválido: {tribunal_id_str}")
                continue
            
            # Verificar si el tribunal existe en nuestra DB (por id)
            tribunal = session.exec(
                select(Tribunal).where(Tribunal.id == tribunal_id_uuid)
            ).first()
            
            # Crear el detalle (vinculando con tribunal si existe)
            receptor_detail = ReceptorDetail(
                receptor_id=receptor.id,
                tribunal_id=tribunal.id if tribunal else None
            )
            
            if not tribunal:
                tribunales_no_encontrados.add(p.get("tribunalName", tribunal_id_str))
            
            session.add(receptor_detail)
            detalles_insertados += 1

        insertados += 1
        
        # Mostrar progreso cada 10 receptores
        if idx % 10 == 0:
            print(f"📝 Procesados: {idx}/{len(receptores)} | Insertados: {insertados} | Omitidos: {omitidos}")

    # Guardar todos los cambios
    session.commit()
    print("\n💾 Guardando cambios en la base de datos...")

print(f"\n{'='*50}")
print(f"✅ Inserción completada.")
print(f"{'='*50}")
print(f"👉 Nuevos receptores insertados: {insertados}")
print(f"👉 Detalles de tribunal insertados: {detalles_insertados}")
print(f"👉 Receptores omitidos (duplicados): {omitidos}")
print(f"⚠️  Tribunales no encontrados en DB: {len(tribunales_no_encontrados)}")

if tribunales_no_encontrados and len(tribunales_no_encontrados) <= 20:
    print(f"\nTribunales no encontrados:")
    for t in sorted(tribunales_no_encontrados):
        print(f"  - {t}")
