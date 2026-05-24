package com.comunidad_zapotal.comunidad_zapotal.ui.eventos

import android.content.Intent
import android.graphics.Color
import android.os.Bundle
import android.view.View
import android.widget.PopupMenu
import androidx.appcompat.widget.SearchView
import androidx.fragment.app.Fragment
import androidx.recyclerview.widget.LinearLayoutManager
import com.comunidad_zapotal.comunidad_zapotal.R
import com.comunidad_zapotal.comunidad_zapotal.adapter.EventoFullAdapter
import com.comunidad_zapotal.comunidad_zapotal.data.model.Evento
import com.comunidad_zapotal.comunidad_zapotal.databinding.FragmentEventosBinding
import com.comunidad_zapotal.comunidad_zapotal.network.RetrofitClient
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import java.text.SimpleDateFormat
import java.util.Calendar
import java.util.Locale

class EventosFragment : Fragment(R.layout.fragment_eventos) {

    private var _binding: FragmentEventosBinding? = null
    private val binding get() = _binding!!

    private lateinit var adapter: EventoFullAdapter
    private var listaOriginal: List<Evento> = emptyList()
    private var esProximosSeleccionado = true
    private var criterioOrden: String = "FECHA_DESC"

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentEventosBinding.bind(view)

        setupRecyclerView()
        setupListeners()
        setupTabs()
        obtenerEventos()
    }

    private fun setupRecyclerView() {
        adapter = EventoFullAdapter(emptyList()) { evento ->
            val intent = Intent(requireContext(), EventoDetalleActivity::class.java).apply {
                putExtra("titulo", evento.titulo)
                putExtra("descripcion", evento.descripcion)
                putExtra("fechaEvento", evento.fecha_evento)
                putExtra("fechaPublicacion", evento.fecha_publicacion)
                putExtra("estado", evento.estado)
                putExtra("autorNombre", "${evento.usuario.nombres} ${evento.usuario.apellidos}")
                putExtra("autorFoto", evento.usuario.foto_perfil_url)
                putExtra("multimedia", ArrayList(evento.multimedia))
            }
            startActivity(intent)
        }

        binding.recyclerTodosEventos.layoutManager = LinearLayoutManager(requireContext())
        binding.recyclerTodosEventos.adapter = adapter
    }

    private fun setupListeners() {
        binding.searchViewEventos.setOnQueryTextListener(object : SearchView.OnQueryTextListener {
            override fun onQueryTextSubmit(query: String?): Boolean = false
            override fun onQueryTextChange(newText: String?): Boolean {
                aplicarFiltros()
                return true
            }
        })

        binding.btnSortEventos.setOnClickListener { view ->
            mostrarMenuOrden(view)
        }
    }

    private fun setupTabs() {
        binding.tabProximos.setOnClickListener {
            if (!esProximosSeleccionado) {
                esProximosSeleccionado = true
                actualizarEstiloTabs()
                aplicarFiltros()
            }
        }

        binding.tabPasados.setOnClickListener {
            if (esProximosSeleccionado) {
                esProximosSeleccionado = false
                actualizarEstiloTabs()
                aplicarFiltros()
            }
        }
    }

    private fun actualizarEstiloTabs() {
        if (esProximosSeleccionado) {
            binding.tabProximos.setTextColor(Color.parseColor("#10B981"))
            binding.tabPasados.setTextColor(Color.parseColor("#9CA3AF"))
            binding.tabIndicator.animate().translationX(0f).setDuration(200).start()
        } else {
            binding.tabProximos.setTextColor(Color.parseColor("#9CA3AF"))
            binding.tabPasados.setTextColor(Color.parseColor("#10B981"))
            
            // Mueve el indicador al segundo tab
            val tabWidth = binding.tabProximos.width.toFloat()
            binding.tabIndicator.animate().translationX(tabWidth).setDuration(200).start()
        }
    }

    private fun mostrarMenuOrden(view: View) {
        val popup = PopupMenu(requireContext(), view)
        popup.menuInflater.inflate(R.menu.menu_sort_eventos, popup.menu)

        popup.setOnMenuItemClickListener { item ->
            when (item.itemId) {
                R.id.sort_az_eventos -> {
                    criterioOrden = "TITULO_AZ"
                    aplicarFiltros()
                    true
                }
                R.id.sort_fecha_eventos -> {
                    criterioOrden = "FECHA_DESC"
                    aplicarFiltros()
                    true
                }
                else -> false
            }
        }
        popup.show()
    }

    private fun obtenerEventos() {
        RetrofitClient.apiService.obtenerEventos().enqueue(object : Callback<List<Evento>> {
            override fun onResponse(call: Call<List<Evento>>, response: Response<List<Evento>>) {
                if (response.isSuccessful) {
                    listaOriginal = response.body() ?: emptyList()
                    aplicarFiltros()
                }
            }
            override fun onFailure(call: Call<List<Evento>>, t: Throwable) {
                t.printStackTrace()
            }
        })
    }

    private fun aplicarFiltros() {
        val query = binding.searchViewEventos.query.toString().lowercase()

        var listaResultante = listaOriginal.filter { evento ->
            val coincideTexto = (evento.titulo ?: "").lowercase().contains(query)
            val esProximo = esEventoProximoOPresente(evento.fecha_evento ?: "")

            if (esProximosSeleccionado) {
                coincideTexto && esProximo
            } else {
                coincideTexto && !esProximo
            }
        }

        listaResultante = when (criterioOrden) {
            "TITULO_AZ" -> listaResultante.sortedBy { it.titulo }
            "FECHA_DESC" -> listaResultante.sortedByDescending { it.fecha_evento }
            else -> listaResultante
        }

        if (listaResultante.isEmpty()) {
            binding.layoutEmptyEventos.visibility = View.VISIBLE
            binding.recyclerTodosEventos.visibility = View.GONE
            binding.txtEmptyMessageEventos.text = if (esProximosSeleccionado) "No hay eventos próximamente" else "No hay eventos pasados"
        } else {
            binding.layoutEmptyEventos.visibility = View.GONE
            binding.recyclerTodosEventos.visibility = View.VISIBLE
        }

        adapter.updateList(listaResultante)
    }

    private fun esEventoProximoOPresente(fechaStr: String): Boolean {
        return try {
            val formato = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
            val fechaEvento = formato.parse(fechaStr) ?: return false
            
            val hoy = Calendar.getInstance()
            hoy.set(Calendar.HOUR_OF_DAY, 0)
            hoy.set(Calendar.MINUTE, 0)
            hoy.set(Calendar.SECOND, 0)
            hoy.set(Calendar.MILLISECOND, 0)

            // Si es hoy o después, es próximo
            !fechaEvento.before(hoy.time)
        } catch (e: Exception) {
            true
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
