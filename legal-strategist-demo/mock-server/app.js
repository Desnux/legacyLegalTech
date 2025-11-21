const express = require('express');
const cors = require("cors");
const bodyParser = require('body-parser');

const app = express();
const PORT = 8090;

app.use(bodyParser.json());

// Configuración de CORS
app.use(
  cors({
    origin: "http://localhost:3000",
    methods: ["GET", "POST", "DELETE", "PUT", "PATCH"],
  })
);

// Mock de datos iniciales
let demandList = Array.from({ length: 20 }, (_, i) => ({
  title: `Demand ${i + 1}`,
  creation_date: new Date().toISOString(),
  index: i + 1,
  author: `Author ${i + 1}`,
  court: `Court ${i + 1}`,
  legal_subject: `Subject ${i + 1}`,
}));

// Validar credenciales
const validateCredentials = (rut, password) => {
  if (rut === '22.222.222-2') return { status: 500, message: 'PJUD not available.' };
  if (rut === '11.111.111-1' && password === '123') return { status: 200 };
  return { status: 401, message: 'Invalid credentials.' };
};

// Endpoint: Obtener lista de demandas
app.post('/v1/extract/demand_list/', (req, res) => {
  const { password, rut } = req.body;

  const validation = validateCredentials(rut, password);
  if (validation.status !== 200) {
    return res.status(validation.status).json({
      status: validation.status,
      message: validation.message,
    });
  }

  res.status(200).json({
    status: 200,
    message: 'List retrieved successfully.',
    data: demandList,
  });
});

// Endpoint: Enviar demanda
app.post('/v1/send/demand/', (req, res) => {
  const { password, rut, index } = req.body;

  const validation = validateCredentials(rut, password);
  if (validation.status !== 200) {
    return res.status(validation.status).json({
      status: validation.status,
      message: validation.message,
    });
  }

  const demandIndex = demandList.findIndex((d) => d.index === index);
  if (demandIndex === -1) {
    return res.status(404).json({
      status: 404,
      message: 'Demand not found.',
    });
  }

  demandList.splice(demandIndex, 1);

  res.status(200).json({
    status: 200,
    message: 'Demand sent successfully.',
  });
});

// Endpoint: Eliminar demanda
app.delete('/v1/send/demand/', (req, res) => {
  const { password, rut, index } = req.body;

  const validation = validateCredentials(rut, password);
  if (validation.status !== 200) {
    return res.status(validation.status).json({
      status: validation.status,
      message: validation.message,
    });
  }

  const demandIndex = demandList.findIndex((d) => d.index === index);
  if (demandIndex === -1) {
    return res.status(404).json({
      status: 404,
      message: 'Demand not found.',
    });
  }

  demandList.splice(demandIndex, 1);

  res.status(200).json({
    status: 200,
    message: 'Demand deleted successfully.',
  });
});

app.listen(PORT, () => {
  console.log(`Mock server running on http://localhost:${PORT}`);
});
