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

class AutoridadFullAdapter(
    private var lista: List<Autoridad>,
    private val onDetalleClick: (Autoridad) -> Unit
) : RecyclerView.Adapter<AutoridadFullAdapter.ViewHolder>() {

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val imagen: ImageView = view.findViewById(R.id.imgAutoridadFull)
        val nombre: TextView = view.findViewById(R.id.txtNombreAutoridadFull)
        val cargo: TextView = view.findViewById(R.id.txtCargoAutoridadFull)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_autoridad_full, parent, false)
        return ViewHolder(view)
    }

    override fun getItemCount(): Int = lista.size

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val autoridad = lista[position]
        holder.nombre.text = "${autoridad.nombres} ${autoridad.apellidos}"
        holder.cargo.text = autoridad.cargo

        Glide.with(holder.itemView.context)
            .load(autoridad.foto_url)
            .placeholder(R.drawable.ic_profile)
            .error(R.drawable.ic_profile)
            .circleCrop()
            .into(holder.imagen)

        holder.itemView.setOnClickListener { onDetalleClick(autoridad) }
    }

    fun updateList(nuevaLista: List<Autoridad>) {
        lista = nuevaLista
        notifyDataSetChanged()
    }
}