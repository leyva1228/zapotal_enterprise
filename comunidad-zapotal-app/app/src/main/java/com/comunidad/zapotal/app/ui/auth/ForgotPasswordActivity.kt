package com.comunidad.zapotal.app.ui.auth

import android.os.Bundle
import android.widget.ImageButton
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.comunidad.zapotal.app.R
import com.comunidad.zapotal.app.network.RetrofitClient
import com.google.android.material.button.MaterialButton
import com.google.android.material.textfield.TextInputEditText
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class ForgotPasswordActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_forgot_password)

        val btnBack = findViewById<ImageButton>(R.id.btnBackForgot)
        val etEmail = findViewById<TextInputEditText>(R.id.etEmailForgot)
        val btnSend = findViewById<MaterialButton>(R.id.btnSendReset)

        btnBack.setOnClickListener { finish() }

        btnSend.setOnClickListener {
            val email = etEmail.text.toString().trim()

            if (email.isEmpty()) {
                Toast.makeText(this, "Ingresa tu correo electrónico", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            val request = mapOf("email" to email)

            RetrofitClient.apiService.forgotPassword(request).enqueue(object : Callback<Void> {
                override fun onResponse(call: Call<Void>, response: Response<Void>) {
                    if (response.isSuccessful) {
                        Toast.makeText(this@ForgotPasswordActivity, 
                            "Si el correo está registrado, recibirás un enlace de recuperación.", 
                            Toast.LENGTH_LONG).show()
                        finish()
                    } else {
                        Toast.makeText(this@ForgotPasswordActivity, "Error al procesar la solicitud", Toast.LENGTH_SHORT).show()
                    }
                }

                override fun onFailure(call: Call<Void>, t: Throwable) {
                    Toast.makeText(this@ForgotPasswordActivity, "Error de conexión: ${t.message}", Toast.LENGTH_LONG).show()
                }
            })
        }
    }
}
