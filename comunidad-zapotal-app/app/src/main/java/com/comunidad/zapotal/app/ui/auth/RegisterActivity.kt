package com.comunidad.zapotal.app.ui.auth

import android.os.Bundle
import android.widget.ImageButton
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.comunidad.zapotal.app.R
import com.comunidad.zapotal.app.data.model.RegisterRequest
import com.comunidad.zapotal.app.data.model.RegisterResponse
import com.comunidad.zapotal.app.network.RetrofitClient
import com.google.android.material.button.MaterialButton
import com.google.android.material.textfield.TextInputEditText
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class RegisterActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_register)

        val btnBack = findViewById<ImageButton>(R.id.btnBackRegister)
        val etNombres = findViewById<TextInputEditText>(R.id.etNombres)
        val etApellidos = findViewById<TextInputEditText>(R.id.etApellidos)
        val etEmail = findViewById<TextInputEditText>(R.id.etEmail)
        val etDni = findViewById<TextInputEditText>(R.id.etDni)
        val etPassword = findViewById<TextInputEditText>(R.id.etPassword)
        val btnRegister = findViewById<MaterialButton>(R.id.btnRegister)
        val btnIrLogin = findViewById<TextView>(R.id.btnIrLogin)

        btnBack.setOnClickListener { finish() }
        btnIrLogin.setOnClickListener { finish() }

        btnRegister.setOnClickListener {
            val nombres = etNombres.text.toString().trim()
            val apellidos = etApellidos.text.toString().trim()
            val email = etEmail.text.toString().trim()
            val dni = etDni.text.toString().trim() 
            val password = etPassword.text.toString().trim()

            // VALIDACIÓN: DNI ES OBLIGATORIO SEGÚN TU SOLICITUD
            if (nombres.isEmpty() || apellidos.isEmpty() || email.isEmpty() || dni.isEmpty() || password.isEmpty()) {
                Toast.makeText(this, "Por favor completa todos los campos, el DNI es obligatorio", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            val request = RegisterRequest(
                nombres = nombres,
                apellidos = apellidos,
                email = email,
                password = password,
                dni = dni
            )

            RetrofitClient.apiService.register(request)
                .enqueue(object : Callback<RegisterResponse> {
                    override fun onResponse(call: Call<RegisterResponse>, response: Response<RegisterResponse>) {
                        if (response.isSuccessful) {
                            // MENSAJE PERSONALIZADO
                            Toast.makeText(this@RegisterActivity, 
                                "¡Te registraste en la app de Comunidad Zapotal! Ahora puedes iniciar sesión.", 
                                Toast.LENGTH_LONG).show()
                            finish()
                        } else {
                            val errorBody = response.errorBody()?.string() ?: "Error en el registro"
                            Toast.makeText(this@RegisterActivity, errorBody, Toast.LENGTH_LONG).show()
                        }
                    }

                    override fun onFailure(call: Call<RegisterResponse>, t: Throwable) {
                        Toast.makeText(this@RegisterActivity, "Error de conexión: ${t.message}", Toast.LENGTH_LONG).show()
                    }
                })
        }
    }
}
