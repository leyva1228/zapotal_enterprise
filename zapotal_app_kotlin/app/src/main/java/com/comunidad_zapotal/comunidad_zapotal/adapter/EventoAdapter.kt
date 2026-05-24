package com.comunidad_zapotal.comunidad_zapotal.adapter

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.bumptech.glide.Glide
import com.comunidad_zapotal.comunidad_zapotal.R
import com.comunidad_zapotal.comunidad_zapotal.data.model.Evento
import java.text.SimpleDateFormat
import java.util.Locale
import kotlin.collections.isNotEmpty
class EventoAdapter(
    private val listaEventos: MutableList<Evento>,
    private val onDetalleClick: (Evento) -> Unit
) : RecyclerView.Adapter<EventoAdapter.EventoViewHolder>() {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): EventoViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_evento, parent, false)
        return EventoViewHolder(view)
    }

    override fun onBindViewHolder(holder: EventoViewHolder, position: Int) {
        val evento = listaEventos[position]

        holder.txtTitulo.text = evento.titulo
        
        // Formatear fecha del evento
        try {
            val formatoEntrada = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
            val fechaDate = formatoEntrada.parse(evento.fecha_evento ?: "")
            val formatoSalida = SimpleDateFormat("dd MMM yyyy", Locale("es", "ES"))
            holder.txtFecha.text = formatoSalida.format(fechaDate!!)
        } catch (e: Exception) {
            holder.txtFecha.text = evento.fecha_evento
        }

        // Formatear fecha de publicación
        try {
            val formatoEntradaPub = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
            val fechaPub = formatoEntradaPub.parse(evento.fecha_publicacion ?: "")
            val formatoSalida = SimpleDateFormat("dd MMM yyyy", Locale("es", "ES"))
            holder.txtPublicado.text = "Publicado el ${formatoSalida.format(fechaPub!!)}"
        } catch (e: Exception) {
            holder.txtPublicado.text = "Publicado: ${evento.fecha_publicacion}"
        }

        // Cargar imagen con Glide
        if (evento.multimedia.isNotEmpty()) {
            Glide.with(holder.itemView.context)
                .load(evento.multimedia[0].archivo_url)
                .placeholder(R.drawable.ic_launcher_background)
                .error(R.drawable.ic_launcher_background)
                .into(holder.imgEvento)
        }

        holder.itemView.setOnClickListener {
            onDetalleClick(evento)
        }
    }

    override fun getItemCount(): Int = listaEventos.size

    class EventoViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val imgEvento: ImageView = itemView.findViewById(R.id.imgEvento)
        val txtTitulo: TextView = itemView.findViewById(R.id.txtTituloEvento)
        val txtFecha: TextView = itemView.findViewById(R.id.txtFechaEvento)
        val txtPublicado: TextView = itemView.findViewById(R.id.txtPublicadoEl)
    }
}