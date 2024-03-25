/*
 * Copyright 2021 Readium Foundation. All rights reserved.
 * Use of this source code is governed by the BSD-style license
 * available in the top-level LICENSE file of the project.
 */

package org.readium.r2.testapp.reader

import android.content.Context
import android.net.Uri
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AlertDialog
import android.os.Bundle
import java.io.IOException
import android.content.ContentUris
import android.database.Cursor
import android.provider.DocumentsContract
import android.provider.MediaStore
import androidx.documentfile.provider.DocumentFile
import android.content.Intent
import android.app.Activity
import android.content.pm.PackageManager
import android.Manifest
import android.util.Log


import android.view.Menu
import android.view.MenuInflater
import android.view.MenuItem
import android.widget.Toast
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import org.readium.r2.lcp.lcpLicense
import org.readium.r2.navigator.Navigator
import org.readium.r2.navigator.preferences.Configurable
import org.readium.r2.shared.ExperimentalReadiumApi
import org.readium.r2.shared.UserException
import org.readium.r2.shared.publication.Locator
import org.readium.r2.shared.publication.Publication
import org.readium.r2.testapp.R
import org.readium.r2.testapp.reader.preferences.UserPreferencesBottomSheetDialogFragment

/*
 * Base reader fragment class
 *
 * Provides common menu items and saves last location on stop.
 */
@OptIn(ExperimentalReadiumApi::class)
abstract class BaseReaderFragment : Fragment() {

    val model: ReaderViewModel by activityViewModels()
    protected val publication: Publication get() = model.publication

    protected abstract val navigator: Navigator

    private val REQUEST_CODE_MANAGE_EXTERNAL_STORAGE = 1001

    private var filePathToWriteAccessibility: String? = null
    private var selectedAccessibilityMode: String? = null

    private var filePathToWriteFont: String? = null
    private var selectedFontIdToLaunch: String? = "Arial"
    private var selectedFontColorIdToLaunch: String? = "black"
    private var selectedBackgroundColorIdToLaunch: String? = "white"


    override fun onCreate(savedInstanceState: Bundle?) {
        setHasOptionsMenu(true)
        super.onCreate(savedInstanceState)

        model.fragmentChannel.receive(this) { event ->
            fun toast(id: Int) {
                Toast.makeText(requireContext(), getString(id), Toast.LENGTH_SHORT).show()
            }

            when (event) {
                is ReaderViewModel.FeedbackEvent.BookmarkFailed -> toast(R.string.bookmark_exists)
                is ReaderViewModel.FeedbackEvent.BookmarkSuccessfullyAdded -> toast(R.string.bookmark_added)
            }
        }
    }

    override fun onHiddenChanged(hidden: Boolean) {
        super.onHiddenChanged(hidden)
        setMenuVisibility(!hidden)
        requireActivity().invalidateOptionsMenu()
    }

    override fun onCreateOptionsMenu(menu: Menu, menuInflater: MenuInflater) {
        menuInflater.inflate(R.menu.menu_reader, menu)

        menu.findItem(R.id.settings).isVisible =
            navigator is Configurable<*, *>

        menu.findItem(R.id.drm).isVisible =
            model.publication.lcpLicense != null
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        when (item.itemId) {
            R.id.toc -> {
                model.activityChannel.send(ReaderViewModel.Event.OpenOutlineRequested)
            }
            R.id.accessibility -> {
                showAccessibilityOptionsDialog(requireContext())
            }
            R.id.fontpersonnalisation -> {
                showfontpersonnalisationOptionsDialog(requireContext())
            }
            R.id.bookmark -> {
                model.insertBookmark(navigator.currentLocator.value)
            }
            R.id.settings -> {
                val settingsModel = checkNotNull(model.settings)
                UserPreferencesBottomSheetDialogFragment(settingsModel, "User Settings")
                    .show(childFragmentManager, "Settings")
            }
            R.id.drm -> {
                model.activityChannel.send(ReaderViewModel.Event.OpenDrmManagementRequested)
            }
            else -> return super.onOptionsItemSelected(item)
        }

        return true
    }

    open fun go(locator: Locator, animated: Boolean) {
        navigator.go(locator, animated)
    }

    private fun showfontpersonnalisationOptionsDialog(context: Context) {
        val fontNamesChoice = arrayOf("Arial", "Helvetica", "Calibri", "Verdana", "Tahoma", "Open Sans", "Luciole")
        val fontNamesId = arrayOf("arial.ttf", "helvetica.ttf", "calibri.ttf", "verdana.ttf", "tahoma.ttf", "opensans.ttf", "Luciole-Regular.ttf")

        val fontColorsChoice = arrayOf("Blue", "Yellow", "Red", "Green", "Purple", "Orange", "Pink", "Turquoise", "Brown", "Cyan", "Magenta", "Gold", "Silver", "Maroon", "Navy", "Black", "White")
        val fontColorsId = arrayOf("blue", "yellow", "red", "green", "purple", "orange", "pink", "turquoise", "brown", "cyan", "magenta", "gold", "silver", "maroon", "navy", "black", "white")

        val backgroundColorsChoice = arrayOf("Blue", "Yellow", "Red", "Green", "Purple", "Orange", "Pink", "Turquoise", "Brown", "Cyan", "Magenta", "Gold", "Silver", "Maroon", "Navy", "Black", "White")
        val backgroundColorsId = arrayOf("blue", "yellow", "red", "green", "purple", "orange", "pink", "turquoise", "brown", "cyan", "magenta", "gold", "silver", "maroon", "navy", "black", "white")

        val builder = AlertDialog.Builder(context)
        builder.setTitle("Personnaliser le Texte des Bulles")

        val categories = arrayOf("Type de police", "Couleur de la police", "Couleur de fond", "Sélectionner le fichier")
        val options = arrayOf(fontNamesChoice, fontColorsChoice, backgroundColorsChoice, arrayOf("Sélectionner le fichier DiViNa"))

        builder.setItems(categories) { _, categoryIndex ->
            val categoryOptions = options[categoryIndex]

            val categoryBuilder = AlertDialog.Builder(context)
            categoryBuilder.setTitle(categories[categoryIndex])
            categoryBuilder.setItems(categoryOptions) { _, which ->
                // Assign the selected option based on the category
                when (categoryIndex) {
                    0 -> selectedFontIdToLaunch = fontNamesId[which]
                    1 -> selectedFontColorIdToLaunch = fontColorsId[which]
                    2 -> selectedBackgroundColorIdToLaunch = backgroundColorsId[which]
                    3 -> {
                        // Open the file picker for selecting file
                        openFileLauncherFont.launch("application/*")
                        return@setItems  // Return immediately after launching file picker
                    }
                }
                // Show the category selection dialog again
                showfontpersonnalisationOptionsDialog(context)
            }
            categoryBuilder.setNegativeButton("Cancel", null)
            val categoryDialog = categoryBuilder.create()
            categoryDialog.show()
        }

        builder.setNegativeButton("Cancel", null)
        val dialog = builder.create()
        dialog.show()
    }

    // Déclarez un launcher pour l'ouverture du sélecteur de fichiers
    private val openFileLauncherFont = registerForActivityResult(ActivityResultContracts.GetContent()) { uri: Uri? ->
        uri?.let { fileUri ->
            // Obtenez le chemin du fichier à partir de l'URI
            val filePath = getPathFromUri(requireContext(), fileUri)

            // Vérifiez si le fichier a l'extension .divina
            if (filePath != null && filePath.endsWith(".divina")) {
                // Lancez le programme Python avec le mode d'accessibilité et le chemin du fichier Divina
                filePathToWriteFont = filePath

                Log.d("Parameter_Debug", "selectedFontIdToLaunch: $selectedFontIdToLaunch")
                Log.d("Parameter_Debug", "filePath: $filePathToWriteFont")
                Log.d("Parameter_Debug", "selectedFontColorIdToLaunch: $selectedFontColorIdToLaunch")
                Log.d("Parameter_Debug", "selectedBackgroundColorIdToLaunch: $selectedBackgroundColorIdToLaunch")
                launchPythonProgramFont(selectedFontIdToLaunch, filePath, selectedFontColorIdToLaunch, selectedBackgroundColorIdToLaunch)
            } else {
                Toast.makeText(requireContext(), "Veuillez sélectionner un fichier .divina", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun launchPythonProgramFont(selectedFontId: String?, filePath: String, fontColorId: String?, backgroundColorId: String?) {

        // Check if permission is already granted
        if (ContextCompat.checkSelfPermission(
                requireActivity(),
                Manifest.permission.MANAGE_EXTERNAL_STORAGE
            ) == PackageManager.PERMISSION_GRANTED
        ) {
            // Permission already granted, launch the Python program
            if (!Python.isStarted()) {
                Python.start(AndroidPlatform(requireActivity()))
            }
            val python = Python.getInstance()
            val mainPersonnalisationModule = python.getModule("main_personnalisation")
            val result = mainPersonnalisationModule.callAttr(
                "main",
                filePath,
                selectedFontId ?: "Arial", // Default font if not provided
                fontColorId ?: "black", // Default font color if not provided
                backgroundColorId ?: "white" // Default background color if not provided
            ).toString()
            Log.d("Parameter_Debug", "les paramètres: $result")
            Toast.makeText(requireActivity(), result, Toast.LENGTH_SHORT).show()

        } else {
            // Permission not granted, request the permission
            requestAccessStoragePermissionLauncherfont.launch(Manifest.permission.MANAGE_EXTERNAL_STORAGE)
        }
    }

    private val requestAccessStoragePermissionLauncherfont = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            // Permission accordée, lancer le programme python
            if (!Python.isStarted()) {
                Python.start(AndroidPlatform(requireActivity()))
            }
            val python = Python.getInstance()
            val mainPersonnalisationModule = python.getModule("main_personnalisation")
            val result = mainPersonnalisationModule.callAttr("main", filePathToWriteFont, selectedFontIdToLaunch, selectedFontColorIdToLaunch, selectedBackgroundColorIdToLaunch).toString()
            Toast.makeText(requireActivity(), result, Toast.LENGTH_SHORT).show()
        } else {
            // La permission a été refusée
            Toast.makeText(requireActivity(), "Permission refusée pour écrire dans le stockage externe", Toast.LENGTH_SHORT).show()
        }
    }
    private fun showAccessibilityOptionsDialog(context: Context) {
        val accessibilityModes = arrayOf("Surbrillance", "Agrandissement", "Agrandissement isolé")
        val accessibilityModesIds = arrayOf("Highlight", "ZoomIn", "ZoomInBlack")

        val builder = AlertDialog.Builder(context)
        builder.setTitle("Choisissez un mode d'accessibilité")
        builder.setItems(accessibilityModes) { _, which ->
            val selectedModeId = accessibilityModesIds[which]
            selectedAccessibilityMode = selectedModeId // Stockez le mode sélectionné

            // Ouvrez le sélecteur de fichiers
            openFileLauncherAccessibility.launch("application/*")
        }
        builder.setNegativeButton("Annuler", null)
        val dialog = builder.create()
        dialog.show()
    }

    // Déclarez un launcher pour l'ouverture du sélecteur de fichiers
    private val openFileLauncherAccessibility = registerForActivityResult(ActivityResultContracts.GetContent()) { uri: Uri? ->
        uri?.let { fileUri ->
            // Obtenez le chemin du fichier à partir de l'URI
            val filePath = getPathFromUri(requireContext(), fileUri)

            // Vérifiez si le fichier a l'extension .divina
            if (filePath != null && filePath.endsWith(".divina")) {
                // Lancez le programme Python avec le mode d'accessibilité et le chemin du fichier Divina
                filePathToWriteAccessibility = filePath

                Log.d("Parameter_Debug", "Path du fichier divina: $filePathToWriteAccessibility")
                Log.d("Parameter_Debug", "Mode d'accéssiblité: $selectedAccessibilityMode")

                launchPythonProgramAccessibility(selectedAccessibilityMode, filePath)
            } else {
                Toast.makeText(requireContext(), "Veuillez sélectionner un fichier .divina", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun getPathFromUri(context: Context, uri: Uri): String? {
        if (DocumentsContract.isDocumentUri(context, uri)) {
            val documentId = DocumentsContract.getDocumentId(uri)
            val split = documentId.split(":")
            if (split.size == 2) {
                val storageType = split[0]
                if ("raw" == storageType) {
                    return split[1]
                } else {
                    val contentUri = when (storageType) {
                        "com.android.externalstorage.documents" -> {
                            val volumeId = split[0]
                            val path = split[1]
                            val rootUri = MediaStore.Files.getContentUri(volumeId)
                            ContentUris.withAppendedId(rootUri, path.toLong())
                        }
                        "com.android.providers.downloads.documents" -> {
                            ContentUris.withAppendedId(
                                Uri.parse("content://downloads/public_downloads"),
                                split[1].toLong()
                            )
                        }
                        else -> uri
                    }
                    context.contentResolver.query(
                        contentUri,
                        arrayOf(MediaStore.Files.FileColumns.DATA),
                        null,
                        null,
                        null
                    )?.use { cursor ->
                        val columnIndex = cursor.getColumnIndex(MediaStore.Files.FileColumns.DATA)
                        val path = if (columnIndex != -1) {
                            cursor.getString(columnIndex)
                        } else {
                            // La colonne n'existe pas dans le curseur
                            null
                        }
                        cursor.close()
                        return path
                    }
                }
            }
        }
        return null
    }

    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            // Permission granted, execute the Python code
            if (!Python.isStarted()) {
                Python.start(AndroidPlatform(requireActivity()))
            }
            val python = Python.getInstance()
            val mainAccessibilityModule = python.getModule("main_accessibility")
            val result = mainAccessibilityModule.callAttr("main", filePathToWriteAccessibility, selectedAccessibilityMode).toString()
            Toast.makeText(requireActivity(), result, Toast.LENGTH_SHORT).show()
        } else {
            // Permission denied, show a toast
            Toast.makeText(requireActivity(), "Permission refusée pour lire et écrire dans le stockage externe.", Toast.LENGTH_SHORT).show()
        }
    }

    // Méthode pour lancer le programme Python
    private fun launchPythonProgramAccessibility(selectedModeId: String?, filePath: String) {
        if (shouldRequestPermission()) {
            if (ActivityCompat.shouldShowRequestPermissionRationale(requireActivity(), Manifest.permission.MANAGE_EXTERNAL_STORAGE)) {
                Toast.makeText(requireActivity(), "La permission d'accès au stockage est nécessaire pour exécuter le programme Python.", Toast.LENGTH_LONG).show()
            } else {
                requestPermissionLauncher.launch(Manifest.permission.MANAGE_EXTERNAL_STORAGE)
            }
        } else {
            // Permission already granted, execute the Python code
            if (!Python.isStarted()) {
                Python.start(AndroidPlatform(requireActivity()))
            }
            val python = Python.getInstance()
            val mainAccessibilityModule = python.getModule("main_accessibility")
            val result = mainAccessibilityModule.callAttr("main", filePath, selectedModeId).toString()
            Toast.makeText(requireActivity(), result, Toast.LENGTH_SHORT).show()
        }
    }

    private fun shouldRequestPermission(): Boolean {
        return ContextCompat.checkSelfPermission(
            requireActivity(),
            Manifest.permission.MANAGE_EXTERNAL_STORAGE
        ) != PackageManager.PERMISSION_GRANTED
    }

    protected fun showError(error: UserException) {
        val context = context ?: return
        Toast.makeText(context, error.getUserMessage(context), Toast.LENGTH_LONG).show()
    }
}

