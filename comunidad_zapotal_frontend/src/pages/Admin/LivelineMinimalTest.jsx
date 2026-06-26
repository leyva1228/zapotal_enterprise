import React from "react";
import { Liveline } from "liveline";
/** * TEST MINIMO: un solo chart con datos hardcoded. * Si esto no renderiza, hay un issue con Liveline o su render en mi entorno. */export default function LivelineMinimalTest() {  const ahora = Math.floor(Date.now() / 1000);
  
const data = [];
  
for (let h = 24;
 h >= 0;
 h--) {    data.push({      time: ahora - h * 3600,      value: 50 + Math.sin(h / 2) * 30 + Math.random() * 10,    });
  }  
const value = data[data.length - 1].value;
  
return (    <div style={{ padding: 24, background: "#f4f6f8", minHeight: "100vh" }}>      <h1>Test minimo Liveline</h1>      <p>Ultimo valor esperado: {value.toFixed(2)}</p>      <div style={{ background: "white", borderRadius: 12, padding: 16, width: 600 }}>        <div style={{ height: 300 }}>          <Liveline            data={data}            value={value}            color="#16a34a"            theme="light"            grid            scrub            fill            badge            window={86400}            formatValue={(v) => v.toFixed(2)}          />        </div>      </div>    </div>  );
}