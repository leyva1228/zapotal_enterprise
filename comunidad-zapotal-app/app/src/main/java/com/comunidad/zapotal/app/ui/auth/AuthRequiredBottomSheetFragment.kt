package com.comunidad.zapotal.app.ui.auth

import android.content.Intent
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import com.comunidad.zapotal.app.databinding.LayoutAuthRequiredBottomSheetBinding
import com.google.android.material.bottomsheet.BottomSheetDialogFragment

class AuthRequiredBottomSheetFragment : BottomSheetDialogFragment() {

    private var _binding: LayoutAuthRequiredBottomSheetBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = LayoutAuthRequiredBottomSheetBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.btnSheetLogin.setOnClickListener {
            startActivity(Intent(requireContext(), LoginActivity::class.java))
            dismiss()
        }

        binding.btnSheetRegister.setOnClickListener {
            startActivity(Intent(requireContext(), RegisterActivity::class.java))
            dismiss()
        }

        binding.btnSheetCancel.setOnClickListener {
            dismiss()
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }

    companion object {
        const val TAG = "AuthRequiredBottomSheet"
    }
}
