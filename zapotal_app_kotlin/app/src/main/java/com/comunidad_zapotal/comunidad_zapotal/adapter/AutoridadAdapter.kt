package com.comunidad_zapotal.comunidad_zapotal.adapter

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.bumptech.glide.Glide
import com.comunidad_zapotal.comunidad_zapotal.R
import com.comunidad_zapotal.comunidad_zapotal.data.model.Autoridad

class AutoridadAdapter(
    private val listaAutoridades: List<Autoridad>
) : RecyclerView.Adapter<AutoridadAdapter.AutoridadViewHolder>() {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): AutoridadViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_autoridad, parent, false)
        return AutoridadViewHolder(view)
    }

    override fun onBindViewHolder(holder: AutoridadViewHolder, position: Int) {
        val autoridad = listaAutoridades[position]

        holder.txtNombre.text = "${autoridad.nombres ?: ""} ${autoridad.apellidos ?: ""}"
        holder.txtCargo.text = autoridad.cargo ?: "Autoridad"

        Glide.with(holder.itemView.context)
            .load(autoridad.foto_url)
            .placeholder(R.drawable.ic_profile)
            .error(R.drawable.ic_profile)
            .circleCrop() // Esto asegura que Glide recorte la imagen en círculo
            .into(holder.imgFoto)
    }

    override fun getItemCount(): Int = listaAutoridades.size

    class AutoridadViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val imgFoto: ImageView = view.findViewById(R.id.imgAutoridad)
        val txtNombre: TextView = view.findViewById(R.id.txtNombreAutoridad)
        val txtCargo: TextView = view.findViewById(R.id.txtCargoAutoridad)
    }
}