package com.comunidad_zapotal.comunidad_zapotal.adapter

import android.content.res.ColorStateList
import android.graphics.Color
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
import java.util.Calendar
import java.util.Locale

class EventoFullAdapter(
    private var lista: List<Evento>,
    private val onDetalleClick: (Evento) -> Unit
) : RecyclerView.Adapter<EventoFullAdapter.ViewHolder>() {

    inner class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val imagen: ImageView = view.findViewById(R.id.imgEvento)
        val titulo: TextView = view.findViewById(R.id.txtTituloEvento)
        val descripcion: TextView = view.findViewById(R.id.txtDescripcionCorta)
        val containerFechaPill: View = view.findViewById(R.id.containerFechaPill)
        val txtFechaEvento: TextView = view.findViewById(R.id.txtFechaEvento)
        val txtPublicado: TextView = view.findViewById(R.id.txtPublicadoEl)

        init {
            itemView.setOnClickListener {
                val position = adapterPosition
                if (position != RecyclerView.NO_POSITION) {
                    onDetalleClick(lista[position])
                }
            }
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_evento_vertical, parent, false)
        return ViewHolder(view)
    }

    override fun getItemCount(): Int = lista.size

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val evento = lista[position]

        holder.titulo.text = evento.titulo
        holder.descripcion.text = evento.descripcion

        // Imagen
        if (evento.multimedia.isNotEmpty()) {
            Glide.with(holder.itemView.context)
                .load(evento.multimedia[0].archivo_url)
                .placeholder(R.drawable.ic_launcher_background)
                .error(R.drawable.ic_launcher_background)
                .into(holder.imagen)
        } else {
            holder.imagen.setImageResource(R.drawable.ic_launcher_background)
        }

        // Fecha evento y estado
        try {
            val formatoEntrada = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
            val fechaEventoDate = formatoEntrada.parse(evento.fecha_evento ?: "")
            val hoy = Calendar.getInstance()
            
            val calEvento = Calendar.getInstance().apply { time = fechaEventoDate!! }
            
            val esHoy = hoy.get(Calendar.YEAR) == calEvento.get(Calendar.YEAR) &&
                    hoy.get(Calendar.DAY_OF_YEAR) == calEvento.get(Calendar.DAY_OF_YEAR)

            if (esHoy) {
                holder.txtFechaEvento.text = "Realizándose ahora mismo"
                holder.containerFechaPill.backgroundTintList = ColorStateList.valueOf(Color.parseColor("#991B1B"))
                holder.txtFechaEvento.setTextColor(Color.WHITE)
            } else {
                val formatoSalida = SimpleDateFormat("dd 'de' MMMM, yyyy", Locale("es", "ES"))
                holder.txtFechaEvento.text = formatoSalida.format(fechaEventoDate!!)
                holder.containerFechaPill.backgroundTintList = ColorStateList.valueOf(Color.parseColor("#064E3B"))
                holder.txtFechaEvento.setTextColor(Color.parseColor("#10B981"))
            }
        } catch (e: Exception) {
            holder.txtFechaEvento.text = evento.fecha_evento
        }

        // Fecha publicación
        try {
            val formatoEntradaPub = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
            val fechaPub = formatoEntradaPub.parse(evento.fecha_publicacion ?: "")
            val formatoSalida = SimpleDateFormat("dd MMM yyyy", Locale("es", "ES"))
            holder.txtPublicado.text = "Publicado el ${formatoSalida.format(fechaPub!!)}"
        } catch (e: Exception) {
            holder.txtPublicado.text = "Publicado el ${evento.fecha_publicacion}"
        }
    }

    fun updateList(nuevaLista: List<Evento>) {
        lista = nuevaLista
        notifyDataSetChanged()
    }
}
