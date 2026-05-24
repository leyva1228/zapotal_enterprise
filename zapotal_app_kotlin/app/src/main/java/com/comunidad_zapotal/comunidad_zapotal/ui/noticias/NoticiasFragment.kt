package com.comunidad_zapotal.comunidad_zapotal.ui.noticias

import android.content.Intent
import android.graphics.Color
import android.os.Bundle
import android.view.View
import android.widget.PopupMenu
import androidx.appcompat.widget.SearchView
import androidx.fragment.app.Fragment
import androidx.recyclerview.widget.LinearLayoutManager
import com.comunidad_zapotal.comunidad_zapotal.R
import com.comunidad_zapotal.comunidad_zapotal.adapter.NoticiaFullAdapter
import com.comunidad_zapotal.comunidad_zapotal.data.model.Noticia
import com.comunidad_zapotal.comunidad_zapotal.databinding.FragmentNoticiasBinding
import com.comunidad_zapotal.comunidad_zapotal.network.RetrofitClient
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import java.text.SimpleDateFormat
import java.util.Calendar
import java.util.Locale
import java.util.concurrent.TimeUnit

class NoticiasFragment : Fragment(R.layout.fragment_noticias) {

    private var _binding: FragmentNoticiasBinding? = null
    private val binding get() = _binding!!

    private lateinit var adapter: NoticiaFullAdapter
    private var listaOriginal: List<Noticia> = emptyList()
    private var esRecientesSeleccionado = true
    private var criterioOrden: String = "FECHA_DESC"

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentNoticiasBinding.bind(view)

        setupRecyclerView()
        setupListeners()
        setupTabs()
        obtenerNoticias()
    }

    private fun setupRecyclerView() {
        adapter = NoticiaFullAdapter(emptyList()) { noticia ->
            abrirDetalleNoticia(noticia)
        }
        binding.recyclerTodasNoticias.layoutManager = LinearLayoutManager(requireContext())
        binding.recyclerTodasNoticias.adapter = adapter
    }

    private fun abrirDetalleNoticia(noticia: Noticia) {
        val intent = Intent(requireContext(), NoticiaDetalleActivity::class.java).apply {
            putExtra("titulo", noticia.titulo)
            putExtra("contenido", noticia.contenido)
            putExtra("fecha", noticia.fecha_publicacion)
            putExtra("estado", noticia.estado) // <-- PASAMOS EL ESTADO REAL
            putExtra("autorNombre", "${noticia.usuario.nombres} ${noticia.usuario.apellidos}")
            putExtra("autorFoto", noticia.usuario.foto_perfil_url)
            putExtra("multimedia", ArrayList(noticia.multimedia))
        }
        startActivity(intent)
    }

    private fun setupListeners() {
        binding.searchViewNoticias.setOnQueryTextListener(object : SearchView.OnQueryTextListener {
            override fun onQueryTextSubmit(query: String?): Boolean = false
            override fun onQueryTextChange(newText: String?): Boolean {
                aplicarFiltros()
                return true
            }
        })

        binding.btnSort.setOnClickListener { view ->
            mostrarMenuOrden(view)
        }
    }

    private fun setupTabs() {
        binding.tabRecientes.setOnClickListener {
            if (!esRecientesSeleccionado) {
                esRecientesSeleccionado = true
                actualizarEstiloTabs()
                aplicarFiltros()
            }
        }

        binding.tabPasadas.setOnClickListener {
            if (esRecientesSeleccionado) {
                esRecientesSeleccionado = false
                actualizarEstiloTabs()
                aplicarFiltros()
            }
        }
    }

    private fun actualizarEstiloTabs() {
        val colorActivo = Color.parseColor("#10B981")
        val colorInactivo = Color.parseColor("#9CA3AF")

        if (esRecientesSeleccionado) {
            binding.tabRecientes.setTextColor(colorActivo)
            binding.tabPasadas.setTextColor(colorInactivo)
            binding.tabIndicator.animate().translationX(0f).setDuration(250).start()
        } else {
            binding.tabRecientes.setTextColor(colorInactivo)
            binding.tabPasadas.setTextColor(colorActivo)
            val tabWidth = binding.tabRecientes.width.toFloat()
            binding.tabIndicator.animate().translationX(tabWidth).setDuration(250).start()
        }
    }

    private fun mostrarMenuOrden(view: View) {
        val popup = PopupMenu(requireContext(), view)
        popup.menuInflater.inflate(R.menu.menu_sort_noticias, popup.menu)

        popup.setOnMenuItemClickListener { item ->
            when (item.itemId) {
                R.id.sort_az -> {
                    criterioOrden = "TITULO_AZ"
                    aplicarFiltros()
                    true
                }
                R.id.sort_fecha -> {
                    criterioOrden = "FECHA_DESC"
                    aplicarFiltros()
                    true
                }
                else -> false
            }
        }
        popup.show()
    }

    private fun obtenerNoticias() {
        RetrofitClient.apiService.obtenerNoticias().enqueue(object : Callback<List<Noticia>> {
            override fun onResponse(call: Call<List<Noticia>>, response: Response<List<Noticia>>) {
                if (response.isSuccessful) {
                    listaOriginal = response.body() ?: emptyList()
                    aplicarFiltros()
                }
            }
            override fun onFailure(call: Call<List<Noticia>>, t: Throwable) {
                t.printStackTrace()
            }
        })
    }

    private fun aplicarFiltros() {
        val query = binding.searchViewNoticias.query.toString().lowercase()

        var listaResultante = listaOriginal.filter { noticia ->
            val coincideTexto = (noticia.titulo ?: "").lowercase().contains(query)
            val esReciente = esNoticiaReciente(noticia.fecha_publicacion ?: "")

            if (esRecientesSeleccionado) {
                coincideTexto && esReciente
            } else {
                coincideTexto && !esReciente
            }
        }

        listaResultante = when (criterioOrden) {
            "TITULO_AZ" -> listaResultante.sortedBy { it.titulo }
            "FECHA_DESC" -> listaResultante.sortedByDescending { it.fecha_publicacion }
            else -> listaResultante
        }

        if (listaResultante.isEmpty()) {
            binding.layoutEmptyNoticias.visibility = View.VISIBLE
            binding.recyclerTodasNoticias.visibility = View.GONE
            binding.txtEmptyMessage.text = if (esRecientesSeleccionado) "No hay noticias recientes" else "No hay noticias pasadas"
        } else {
            binding.layoutEmptyNoticias.visibility = View.GONE
            binding.recyclerTodasNoticias.visibility = View.VISIBLE
        }

        adapter.updateList(listaResultante)
    }

    private fun esNoticiaReciente(fechaStr: String): Boolean {
        return try {
            val formato = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
            val fechaNoticia = formato.parse(fechaStr.split("T")[0]) ?: return false
            val hoy = Calendar.getInstance().time
            val diffInMillis = hoy.time - fechaNoticia.time
            val diffInDays = TimeUnit.MILLISECONDS.toDays(diffInMillis)
            diffInDays <= 7
        } catch (e: Exception) {
            true
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
