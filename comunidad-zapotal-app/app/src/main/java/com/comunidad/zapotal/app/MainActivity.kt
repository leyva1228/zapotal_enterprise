package com.comunidad.zapotal.app

import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.GravityCompat
import androidx.navigation.fragment.NavHostFragment
import androidx.navigation.ui.setupWithNavController
import com.comunidad.zapotal.app.databinding.ActivityMainBinding

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        val navHostFragment =
            supportFragmentManager.findFragmentById(R.id.nav_host_fragment) as NavHostFragment

        val navController = navHostFragment.navController

        // Configurar Bottom Navigation
        binding.bottomNavigation.setupWithNavController(navController)

        // Configurar Navigation Drawer
        binding.navView.setNavigationItemSelectedListener { menuItem ->
            when (menuItem.itemId) {
                R.id.nav_info -> Toast.makeText(this, "Mi información", Toast.LENGTH_SHORT).show()
                R.id.nav_reportes -> Toast.makeText(this, "Mis reportes", Toast.LENGTH_SHORT).show()
                R.id.nav_notificaciones -> Toast.makeText(this, "Notificaciones", Toast.LENGTH_SHORT).show()
                R.id.nav_privacidad -> Toast.makeText(this, "Privacidad", Toast.LENGTH_SHORT).show()
                R.id.nav_configuracion -> Toast.makeText(this, "Configuración", Toast.LENGTH_SHORT).show()
                R.id.nav_ayuda -> Toast.makeText(this, "Ayuda y soporte", Toast.LENGTH_SHORT).show()
                R.id.nav_logout -> Toast.makeText(this, "Cerrar Sesión", Toast.LENGTH_SHORT).show()
            }
            binding.drawerLayout.closeDrawer(GravityCompat.START)
            true
        }
    }

    // Método para abrir el drawer desde los fragmentos
    fun openDrawer() {
        binding.drawerLayout.openDrawer(GravityCompat.START)
    }
}