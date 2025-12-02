from __future__ import annotations

import json
import logging
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from config import Config
from models.pydantic import PropertyDataResponse, OwnerDetailResponse
from models.pydantic import OwnedPropertyDetailed
from models.pydantic.homespotter_owner import OwnedSociety
from models.pydantic import TenantReportResponse
from models.pydantic.homespotter_tenant import ActiveVehicle


class HomeSpotterService:
    """Wrapper around HomeSpotter API endpoints used by the project."""

    DEFAULT_BASE_URL = Config.HOMESPOTTER_BASE_URL
    DEFAULT_API_KEY = Config.HOMESPOTTER_API_KEY
    DEFAULT_TIMEOUT = 60  # Reduced from 360 to 60 seconds (more reasonable default)
    MAX_WORKERS = 10  # Max concurrent requests for parallel property fetching

    def __init__(self, api_key: str | None = None, base_url: str | None = None, timeout: int = DEFAULT_TIMEOUT) -> None:
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.api_key = api_key or self.DEFAULT_API_KEY
        self.timeout = timeout

        if not self.api_key:
            raise ValueError(
                "Missing HomeSpotter API key. Provide it via parameter or HOMESPOTTER_API_KEY env var."
            )
        
        # Create a session for connection pooling and reuse
        self._session = requests.Session()
        self._session.headers.update({
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
        })
        
        # Track HTTP call times for statistics
        self._http_call_times: dict[str, list[float]] = {}  # endpoint -> list of call times

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def get_property_data(self, comuna_code: str, rol: str) -> PropertyDataResponse:
        """Return enriched property information by *comuna_code* and *rol*."""
        start_time = time.time()
        logging.info(f"🏠 [HomeSpotter] Iniciando get_property_data para ROL {rol} (comunaCode: {comuna_code})")
        
        payload = {"comunaCode": comuna_code, "rol": rol}
        data = self._post("/get_property_data", payload)
        result = PropertyDataResponse.model_validate(data)
        
        elapsed = round(time.time() - start_time, 4)
        logging.info(f"🏠 [HomeSpotter] get_property_data completado en {elapsed:.4f}s para ROL {rol}")
        
        # Note: HTTP statistics are logged at the parent method level (e.g., list_person_properties)
        # to avoid log spam when called in parallel
        
        return result

    def get_owner_data(self, rut: str, log_stats: bool = True) -> OwnerDetailResponse:
        """Return owner details by *rut*.
        
        Args:
            rut: RUT to query
            log_stats: If True, log HTTP statistics. Set to False when called from 
                      list_person_properties to avoid clearing stats prematurely.
        """
        start_time = time.time()
        logging.info(f"🏠 [HomeSpotter] Iniciando get_owner_data para RUT {rut}")
        
        payload = {"rut": rut}
        data = self._post("/get_owner_data", payload)
        result = OwnerDetailResponse.model_validate(data)
        
        elapsed = round(time.time() - start_time, 4)
        properties_count = len(result.ownedProperties) if result.ownedProperties else 0
        societies_count = len(result.ownedSocieties) if result.ownedSocieties else 0
        
        # Log HTTP call statistics only if requested (not when called from list_person_properties)
        if log_stats:
            logging.info("")
            logging.info("=" * 80)
            logging.info(f"🏠 [HomeSpotter] RESUMEN: get_owner_data para RUT {rut}")
            logging.info("=" * 80)
            logging.info(f"  ⏱️  Tiempo total:              {elapsed:.4f}s")
            logging.info(f"  📋 Propiedades encontradas:    {properties_count}")
            logging.info(f"  🏢 Sociedades encontradas:     {societies_count}")
            self._log_http_statistics("get_owner_data")
            logging.info("=" * 80)
            logging.info("")
        else:
            logging.info(f"🏠 [HomeSpotter] get_owner_data completado en {elapsed:.4f}s para RUT {rut} - {properties_count} propiedades, {societies_count} sociedades")
        
        return result

    def get_tenant_report(self, rut: str, log_stats: bool = True) -> TenantReportResponse:
        """Return a Tenant/Company risk report for the given *rut*.
        
        Args:
            rut: RUT to query
            log_stats: If True, log HTTP statistics. Set to False when called from 
                      list_person_vehicles to avoid clearing stats prematurely.
        """
        start_time = time.time()
        logging.info(f"🏠 [HomeSpotter] Iniciando get_tenant_report para RUT {rut}")
        
        payload = {"rut": rut}
        data = self._post("/get_tenant_report", payload)
        result = TenantReportResponse.model_validate(data)
        
        elapsed = round(time.time() - start_time, 4)
        vehicles_count = len(result.actives.vehicles) if result.actives and result.actives.vehicles else 0
        
        # Log HTTP call statistics only if requested
        if log_stats:
            logging.info("")
            logging.info("=" * 80)
            logging.info(f"🏠 [HomeSpotter] RESUMEN: get_tenant_report para RUT {rut}")
            logging.info("=" * 80)
            logging.info(f"  ⏱️  Tiempo total:              {elapsed:.4f}s")
            logging.info(f"  🚗 Vehículos encontrados:      {vehicles_count}")
            self._log_http_statistics("get_tenant_report")
            logging.info("=" * 80)
            logging.info("")
        else:
            logging.info(f"🏠 [HomeSpotter] get_tenant_report completado en {elapsed:.4f}s para RUT {rut} - {vehicles_count} vehículos")
        
        return result

    # ------------------------------------------------------------------
    # Aggregated helpers (compose the two official endpoints)
    # ------------------------------------------------------------------

    def list_person_societies(self, rut: str) -> list[OwnedSociety]:
        """Return the societies where the person identified by *rut* is owner or shareholder.

        This is extracted directly from the *ownedSocieties* field present in the
        response of the `/get_owner_data` endpoint.
        """
        start_time = time.time()
        logging.info(f"🏠 [HomeSpotter] Iniciando list_person_societies para RUT {rut}")
        
        owner_resp = self.get_owner_data(rut, log_stats=False)
        result = owner_resp.ownedSocieties
        
        elapsed = round(time.time() - start_time, 4)
        
        logging.info("")
        logging.info("=" * 80)
        logging.info(f"🏠 [HomeSpotter] RESUMEN: list_person_societies para RUT {rut}")
        logging.info("=" * 80)
        logging.info(f"  ⏱️  Tiempo total:              {elapsed:.4f}s")
        logging.info(f"  🏢 Sociedades encontradas:     {len(result)}")
        self._log_http_statistics("list_person_societies")
        logging.info("=" * 80)
        logging.info("")
        
        return result

    def list_person_properties(self, rut: str) -> list[OwnedPropertyDetailed]:
        """Return the properties of the person with full address, *foja*, number and year.

        The method works in two steps:
        1. Use `/get_owner_data` to obtain the basic list of properties (rol, comunaCode).
        2. For each property, call `/get_property_data` to enrich it with registration
           information (*foja*, *number*, *year*). If the transaction information is
           missing, the registration fields are returned as empty strings.
        
        Optimized: Property detail calls are made in parallel for better performance.
        """
        method_start_time = time.time()
        logging.info(f"🏠 [HomeSpotter] Iniciando list_person_properties para RUT {rut}")
        
        # Clear HTTP statistics at the start to track all calls in this method
        self._http_call_times.clear()

        owner_resp = self.get_owner_data(rut, log_stats=False)
        
        if not owner_resp.ownedProperties:
            elapsed = round(time.time() - method_start_time, 4)
            logging.info(f"🏠 [HomeSpotter] list_person_properties completado en {elapsed:.4f}s para RUT {rut} - 0 propiedades")
            return []
        
        properties_to_fetch = list(owner_resp.ownedProperties)
        total_properties = len(properties_to_fetch)
        logging.info(f"🏠 [HomeSpotter] Obteniendo detalles de {total_properties} propiedades en paralelo (max {min(self.MAX_WORKERS, total_properties)} workers)")
        
        # Parallelize property detail fetching
        detailed_properties: list[OwnedPropertyDetailed] = []
        properties_fetched = 0
        properties_failed = 0
        parallel_start_time = time.time()
        property_call_times: list[float] = []  # Track individual call times
        
        def fetch_property_data(prop) -> tuple[Any, PropertyDataResponse | None, float]:
            """Helper to fetch property data, returns (prop, prop_data or None, call_time)."""
            call_start = time.time()
            try:
                prop_data = self.get_property_data(prop.comunaCode, prop.rol)
                call_time = round(time.time() - call_start, 4)
                return (prop, prop_data, call_time)
            except Exception as e:
                call_time = round(time.time() - call_start, 4)
                logging.warning(
                    f"🏠 [HomeSpotter] Error obteniendo datos de propiedad ROL {prop.rol} (comunaCode: {prop.comunaCode}) después de {call_time:.4f}s: {e}"
                )
                return (prop, None, call_time)
        
        # Fetch all property details in parallel
        with ThreadPoolExecutor(max_workers=min(self.MAX_WORKERS, len(properties_to_fetch))) as executor:
            future_to_prop = {
                executor.submit(fetch_property_data, prop): prop 
                for prop in properties_to_fetch
            }
            
            for future in as_completed(future_to_prop):
                prop, prop_data, call_time = future.result()
                property_call_times.append(call_time)
                
                if prop_data is None:
                    properties_failed += 1
                    continue

                properties_fetched += 1

                # Address: prefer the SII formatted address, fallback to owner list address
                address = prop_data.siiData.address or prop.address

                # Registration details (foja, number, year) – use first history item when available
                foja = number = year = ""
                if prop_data.marketData.propertyHistory:
                    history_item = prop_data.marketData.propertyHistory[0]
                    foja = history_item.transactionFojas or ""
                    number = history_item.transactionNumber or ""
                    year = history_item.transactionYear or ""

                detailed_properties.append(
                    OwnedPropertyDetailed(
                        address=address,
                        rol=prop.rol,
                        comuna=prop.comuna,
                        comunaCode=prop.comunaCode,
                        foja=foja,
                        number=number,
                        year=year,
                    )
                )

        parallel_elapsed = round(time.time() - parallel_start_time, 4)
        total_elapsed = round(time.time() - method_start_time, 4)
        
        # Calculate and log statistics
        logging.info("")
        logging.info("=" * 80)
        logging.info(f"🏠 [HomeSpotter] RESUMEN: list_person_properties para RUT {rut}")
        logging.info("=" * 80)
        logging.info(f"  ⏱️  Tiempo total:              {total_elapsed:.4f}s")
        logging.info(f"  ✅ Propiedades exitosas:       {properties_fetched}/{total_properties}")
        if properties_failed > 0:
            logging.info(f"  ❌ Propiedades fallidas:        {properties_failed}")
        
        if property_call_times:
            min_time = min(property_call_times)
            max_time = max(property_call_times)
            avg_time = sum(property_call_times) / len(property_call_times)
            total_calls_time = sum(property_call_times)
            speedup = total_calls_time / parallel_elapsed if parallel_elapsed > 0 else 1.0
            
            logging.info("")
            logging.info("  📊 Estadísticas de llamadas get_property_data:")
            logging.info(f"     • Total de llamadas:        {len(property_call_times)}")
            logging.info(f"     • Tiempo total (suma):      {total_calls_time:.4f}s")
            logging.info(f"     • Tiempo paralelo (real):   {parallel_elapsed:.4f}s")
            logging.info(f"     • Aceleración:              {speedup:.2f}x")
            logging.info(f"     • Tiempo promedio:          {avg_time:.4f}s")
            logging.info(f"     • Tiempo mínimo:            {min_time:.4f}s")
            logging.info(f"     • Tiempo máximo:            {max_time:.4f}s")
            
            # Log individual call times (limit to first 10 to avoid log spam)
            if len(property_call_times) <= 10:
                times_str = ", ".join([f"{t:.4f}s" for t in property_call_times])
                logging.info(f"     • Tiempos individuales:     [{times_str}]")
            else:
                first_5 = ", ".join([f"{t:.4f}s" for t in property_call_times[:5]])
                logging.info(f"     • Primeros 5 tiempos:       [{first_5}, ... ({len(property_call_times) - 5} más)]")
        
        # Log HTTP call statistics
        self._log_http_statistics("list_person_properties")
        logging.info("=" * 80)
        logging.info("")
        
        return detailed_properties

    def list_person_vehicles(self, rut: str) -> list[ActiveVehicle]:
        """Return the vehicles registered to *rut* using the tenant report data."""
        start_time = time.time()
        logging.info(f"🏠 [HomeSpotter] Iniciando list_person_vehicles para RUT {rut}")
        
        # Clear HTTP stats to track only calls from this method
        self._http_call_times.clear()
        report = self.get_tenant_report(rut, log_stats=False)
        result = report.actives.vehicles if report.actives and report.actives.vehicles else []
        
        elapsed = round(time.time() - start_time, 4)
        
        logging.info("")
        logging.info("=" * 80)
        logging.info(f"🏠 [HomeSpotter] RESUMEN: list_person_vehicles para RUT {rut}")
        logging.info("=" * 80)
        logging.info(f"  ⏱️  Tiempo total:              {elapsed:.4f}s")
        logging.info(f"  🚗 Vehículos encontrados:      {len(result)}")
        self._log_http_statistics("list_person_vehicles")
        logging.info("=" * 80)
        logging.info("")
        
        return result

    # ------------------------------------------------------------------
    # Internal request helpers
    # ------------------------------------------------------------------

    def _post(self, endpoint: str, json_payload: dict[str, Any]) -> Any:
        """Make a POST request using the session for connection reuse."""
        url = f"{self.base_url}{endpoint}"
        request_start = time.time()
        
        try:
            response = self._session.post(url, json=json_payload, timeout=self.timeout)
            request_time = round(time.time() - request_start, 4)
            
            # Track call time for statistics
            if endpoint not in self._http_call_times:
                self._http_call_times[endpoint] = []
            self._http_call_times[endpoint].append(request_time)
            
            if response.status_code != 200:
                error_text = response.text[:200] if response.text else "(sin contenido)"
                logging.error(
                    f"🏠 [HomeSpotter] {endpoint} [{request_time:.4f}s] "
                    f"ERROR ({response.status_code}): {error_text}"
                )
                raise ValueError(f"Request failed ({response.status_code}) for {url}: {error_text}")
            
            # Parse response
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                logging.warning(f"🏠 [HomeSpotter] Respuesta no es JSON válido para {endpoint}")
                response_data = {"raw_response": response.text[:500]}
            
            # Log only time
            logging.info(f"🏠 [HomeSpotter] {endpoint} [{request_time:.4f}s]")
            
            return response_data
        except requests.exceptions.Timeout:
            request_time = round(time.time() - request_start, 4)
            # Track failed call time too
            if endpoint not in self._http_call_times:
                self._http_call_times[endpoint] = []
            self._http_call_times[endpoint].append(request_time)
            logging.error(f"🏠 [HomeSpotter] Timeout después de {request_time:.4f}s para {endpoint} (timeout configurado: {self.timeout}s)")
            raise
        except Exception as e:
            request_time = round(time.time() - request_start, 4)
            # Track failed call time too
            if endpoint not in self._http_call_times:
                self._http_call_times[endpoint] = []
            self._http_call_times[endpoint].append(request_time)
            logging.error(f"🏠 [HomeSpotter] Error en POST {endpoint} después de {request_time:.4f}s: {type(e).__name__}: {e}")
            raise
    
    def _log_http_statistics(self, method_name: str):
        """Log statistics for all HTTP calls made during a method execution."""
        if not self._http_call_times:
            return
        
        logging.info("  📡 Estadísticas HTTP por endpoint:")
        for endpoint, times in self._http_call_times.items():
            if times:
                total_calls = len(times)
                total_time = sum(times)
                avg_time = total_time / total_calls
                min_time = min(times)
                max_time = max(times)
                
                logging.info(f"     └─ {endpoint}:")
                logging.info(f"        • Llamadas:              {total_calls}")
                logging.info(f"        • Tiempo total:          {total_time:.4f}s")
                logging.info(f"        • Tiempo promedio:       {avg_time:.4f}s")
                logging.info(f"        • Tiempo mínimo:         {min_time:.4f}s")
                logging.info(f"        • Tiempo máximo:         {max_time:.4f}s")
        
        # Clear statistics after logging
        self._http_call_times.clear()
    
    def __del__(self):
        """Clean up session on deletion."""
        if hasattr(self, '_session'):
            self._session.close() 