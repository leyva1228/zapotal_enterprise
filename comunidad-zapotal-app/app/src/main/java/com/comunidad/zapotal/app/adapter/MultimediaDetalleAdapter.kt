package com.comunidad.zapotal.app.adapter

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import androidx.recyclerview.widget.RecyclerView
import com.bumptech.glide.Glide
import com.comunidad.zapotal.app.R
import com.comunidad.zapotal.app.data.model.Multimedia

class MultimediaDetalleAdapter(
    private val listaMultimedia: List<Multimedia>
) : RecyclerView.Adapter<MultimediaDetalleAdapter.ViewHolder>() {

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val imagen: ImageView = view.findViewById(R.id.imgMultimedia)
        val playIcon: ImageView = view.findViewById(R.id.imgPlayIcon)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_multimedia_detalle, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = listaMultimedia[position]

        // Cargar imagen
        Glide.with(holder.itemView.context)
            .load(item.archivo_url)
            .placeholder(R.drawable.ic_launcher_background)
            .centerCrop()
            .into(holder.imagen)

        // Mostrar icono de play si el tipo es video
        if (item.tipo.lowercase().contains("video")) {
            holder.playIcon.visibility = View.VISIBLE
        } else {
            holder.playIcon.visibility = View.GONE
        }
    }

    override fun getItemCount(): Int = listaMultimedia.size
}