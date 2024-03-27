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

    // Méthode pour afficher la boîte de dialogue des options de personnalisation de la police
    private fun showfontpersonnalisationOptionsDialog(context: Context) {
        // Listes des noms de police et de leurs identifiants
        val fontNamesChoice = arrayOf("Arial", "Helvetica", "Calibri", "Verdana", "Tahoma", "Open Sans", "Luciole")
        val fontNamesId = arrayOf("arial.ttf", "helvetica.ttf", "calibri.ttf", "verdana.ttf", "tahoma.ttf", "opensans.ttf", "Luciole-Regular.ttf")

        // Listes des couleurs de police et de leurs identifiants
        val fontColorsChoice = arrayOf("Blue", "Yellow", "Red", "Green", "Purple", "Orange", "Pink", "Turquoise", "Brown", "Cyan", "Magenta", "Gold", "Silver", "Maroon", "Navy", "Black", "White")
        val fontColorsId = arrayOf("blue", "yellow", "red", "green", "purple", "orange", "pink", "turquoise", "brown", "cyan", "magenta", "gold", "silver", "maroon", "navy", "black", "white")

        // Listes des couleurs de fond et de leurs identifiants
        val backgroundColorsChoice = arrayOf("Blue", "Yellow", "Red", "Green", "Purple", "Orange", "Pink", "Turquoise", "Brown", "Cyan", "Magenta", "Gold", "Silver", "Maroon", "Navy", "Black", "White")
        val backgroundColorsId = arrayOf("blue", "yellow", "red", "green", "purple", "orange", "pink", "turquoise", "brown", "cyan", "magenta", "gold", "silver", "maroon", "navy", "black", "white")

        // Création du constructeur de la boîte de dialogue
        val builder = AlertDialog.Builder(context)
        builder.setTitle("Personnaliser le Texte des Bulles")

        // Catégories des options de personnalisation
        val categories = arrayOf("Type de police", "Couleur de la police", "Couleur de fond", "Sélectionner le fichier")
        val options = arrayOf(fontNamesChoice, fontColorsChoice, backgroundColorsChoice, arrayOf("Sélectionner le fichier DiViNa"))

        // Affichage des catégories dans la boîte de dialogue
        builder.setItems(categories) { _, categoryIndex ->
            val categoryOptions = options[categoryIndex]

            // Constructeur pour la sélection des options de chaque catégorie
            val categoryBuilder = AlertDialog.Builder(context)
            categoryBuilder.setTitle(categories[categoryIndex])
            categoryBuilder.setItems(categoryOptions) { _, which ->

                // Attribution de l'option sélectionnée en fonction de la catégorie
                when (categoryIndex) {
                    0 -> selectedFontIdToLaunch = fontNamesChoice[which]
                    1 -> selectedFontColorIdToLaunch = fontColorsId[which]
                    2 -> selectedBackgroundColorIdToLaunch = backgroundColorsId[which]
                    3 -> {
                        // Ouvrir le sélecteur de fichier pour sélectionner un fichier
                        openFileLauncherFont.launch("application/*")
                        return@setItems  // Retourner immédiatement après l'ouverture du sélecteur de fichier
                    }
                }
                // Afficher à nouveau la boîte de dialogue de sélection de catégorie
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

    // Déclaration d'un launcher pour l'ouverture du sélecteur de fichiers
    private val openFileLauncherFont = registerForActivityResult(ActivityResultContracts.GetContent()) { uri: Uri? ->
        uri?.let { fileUri ->
            // Obtention du chemin du fichier à partir de l'URI
            val filePath = getPathFromUri(requireContext(), fileUri)

            // Vérification si le fichier a l'extension .divina
            if (filePath != null && filePath.endsWith(".divina")) {
                // Lancement du programme Python avec les informations de personnalisation des bulles et le chemin du fichier Divina
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

    // Méthode pour lancer le programme Python avec les paramètres de personnalisation de la police
    private fun launchPythonProgramFont(selectedFontId: String?, filePath: String, fontColorId: String?, backgroundColorId: String?) {

        // Vérifier si la permission est déjà accordée
        if (ContextCompat.checkSelfPermission(
                requireActivity(),
                Manifest.permission.MANAGE_EXTERNAL_STORAGE
            ) == PackageManager.PERMISSION_GRANTED
        ) {
            // La permission est déjà accordée, lancer le programme Python
            if (!Python.isStarted()) {
                Python.start(AndroidPlatform(requireActivity()))
            }
            val python = Python.getInstance()
            val mainPersonnalisationModule = python.getModule("main_personnalisation")
            val result = mainPersonnalisationModule.callAttr(
                "main",
                filePath,
                selectedFontId ?: "Arial", // Police par défaut si non fournie
                fontColorId ?: "black", // Couleur de police par défaut si non fournie
                backgroundColorId ?: "white" // Couleur de fond par défaut si non fournie
            ).toString()
            Log.d("Parameter_Debug", "les paramètres: $result")
            Toast.makeText(requireActivity(), result, Toast.LENGTH_SHORT).show()

        } else {
            // La permission n'est pas accordée, demander la permission
            requestAccessStoragePermissionLauncherfont.launch(Manifest.permission.MANAGE_EXTERNAL_STORAGE)
        }
    }

    // Launcher pour demander l'autorisation d'accès au stockage pour l'exécution du programme Python
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

    // Méthode pour afficher la boîte de dialogue des options d'accessibilité
    private fun showAccessibilityOptionsDialog(context: Context) {
        // Options de modes d'accessibilité et leurs identifiants
        val accessibilityModes = arrayOf("Surbrillance", "Agrandissement", "Agrandissement isolé")
        val accessibilityModesIds = arrayOf("Highlight", "ZoomIn", "ZoomInBlack")

        // Création du constructeur de la boîte de dialogue
        val builder = AlertDialog.Builder(context)
        builder.setTitle("Choisissez un mode d'accessibilité")

        // Affichage des options de modes d'accessibilité dans la boîte de dialogue
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

    // Déclaration un launcher pour l'ouverture du sélecteur de fichiers
    private val openFileLauncherAccessibility = registerForActivityResult(ActivityResultContracts.GetContent()) { uri: Uri? ->
        uri?.let { fileUri ->
            // Obtention du chemin du fichier à partir de l'URI
            val filePath = getPathFromUri(requireContext(), fileUri)

            // Vérification si le fichier a l'extension .divina
            if (filePath != null && filePath.endsWith(".divina")) {
                // Lancement du programme Python avec le mode d'accessibilité et le chemin du fichier Divina
                filePathToWriteAccessibility = filePath

                Log.d("Parameter_Debug", "Path du fichier divina: $filePathToWriteAccessibility")
                Log.d("Parameter_Debug", "Mode d'accéssiblité: $selectedAccessibilityMode")

                launchPythonProgramAccessibility(selectedAccessibilityMode, filePath)
            } else {
                Toast.makeText(requireContext(), "Veuillez sélectionner un fichier .divina", Toast.LENGTH_SHORT).show()
            }
        }
    }

    // Méthode pour obtenir le chemin du fichier à partir de son URI
    private fun getPathFromUri(context: Context, uri: Uri): String? {
        // Vérifier si l'URI correspond à un document
        if (DocumentsContract.isDocumentUri(context, uri)) {
            val documentId = DocumentsContract.getDocumentId(uri) // Obtenir l'identifiant du document
            val split = documentId.split(":") // Séparer l'identifiant du type de stockage

            // Vérifier si l'identifiant est au bon format
            if (split.size == 2) {
                val storageType = split[0] // Récupérer le type de stockage

                // Si le type de stockage est "raw", le chemin est directement spécifié
                if ("raw" == storageType) {
                    return split[1] // Retourner le chemin du fichier
                } else {
                    val contentUri = when (storageType) { // Déterminer le type de contenu de l'URI
                        // Si le type de stockage est externe
                        "com.android.externalstorage.documents" -> {
                            val volumeId = split[0] // Récupérer l'identifiant du volume
                            val path = split[1] // Récupérer le chemin
                            val rootUri = MediaStore.Files.getContentUri(volumeId) // Obtenir l'URI de base du stockage externe
                            ContentUris.withAppendedId(rootUri, path.toLong()) // Créer l'URI du fichier
                        }
                        // Si le type de stockage est les téléchargements
                        "com.android.providers.downloads.documents" -> {
                            // Obtenir l'URI du fichier à partir de l'identifiant du document
                            ContentUris.withAppendedId(
                                Uri.parse("content://downloads/public_downloads"),
                                split[1].toLong()
                            )
                        }
                        // Si le type de stockage n'est pas pris en charge, utiliser directement l'URI fournie
                        else -> uri
                    }
                    // Effectuer une requête pour obtenir le chemin réel du fichier à partir de l'URI
                    context.contentResolver.query(
                        contentUri,
                        arrayOf(MediaStore.Files.FileColumns.DATA), // Demander la colonne de données (chemin du fichier)
                        null,
                        null,
                        null
                    )?.use { cursor ->
                        val columnIndex = cursor.getColumnIndex(MediaStore.Files.FileColumns.DATA) // Obtenir l'indice de la colonne de données
                        val path = if (columnIndex != -1) { // Vérifier si la colonne existe dans le curseur
                            cursor.getString(columnIndex) // Récupérer le chemin du fichier à partir du curseur
                        } else {
                            // La colonne n'existe pas dans le curseur
                            null
                        }
                        cursor.close()
                        return path // Retourner le chemin du fichier
                    }
                }
            }
        }
        return null
    }

    // Launcher pour demander la permission d'accès au stockage pour l'exécution du programme Python
    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted ->

        if (isGranted) {
            // Si la permission est accordée, Exécuter le code Python
            if (!Python.isStarted()) {
                Python.start(AndroidPlatform(requireActivity()))
            }
            val python = Python.getInstance()
            val mainAccessibilityModule = python.getModule("main_accessibility")
            val result = mainAccessibilityModule.callAttr("main", filePathToWriteAccessibility, selectedAccessibilityMode).toString()
            Toast.makeText(requireActivity(), result, Toast.LENGTH_SHORT).show() // Afficher le résultat dans un toast
        } else {
            // Si la permission est refusée, Afficher un toast informant que la permission est refusée
            Toast.makeText(requireActivity(), "Permission refusée pour lire et écrire dans le stockage externe.", Toast.LENGTH_SHORT).show()
        }
    }

    // Méthode pour lancer le programme Python avec les paramètres d'accessibilité sélectionnés
    private fun launchPythonProgramAccessibility(selectedModeId: String?, filePath: String) {
        if (shouldRequestPermission()) {
            // Vérifier si la permission doit être demandée
            if (ActivityCompat.shouldShowRequestPermissionRationale(requireActivity(), Manifest.permission.MANAGE_EXTERNAL_STORAGE)) {
                // Afficher un message si l'autorisation est nécessaire
                Toast.makeText(requireActivity(), "La permission d'accès au stockage est nécessaire pour exécuter le programme Python.", Toast.LENGTH_LONG).show()
            } else {
                // Demander la permission d'accès au stockage
                requestPermissionLauncher.launch(Manifest.permission.MANAGE_EXTERNAL_STORAGE)
            }
        } else {
            // La permission est déjà accordée, exécuter le code Python
            if (!Python.isStarted()) {
                Python.start(AndroidPlatform(requireActivity()))
            }
            val python = Python.getInstance()
            val mainAccessibilityModule = python.getModule("main_accessibility")
            val result = mainAccessibilityModule.callAttr("main", filePath, selectedModeId).toString()
            Toast.makeText(requireActivity(), result, Toast.LENGTH_SHORT).show()
        }
    }

    // Méthode pour vérifier si la permission doit être demandée
    private fun shouldRequestPermission(): Boolean {
        return ContextCompat.checkSelfPermission(
            requireActivity(),
            Manifest.permission.MANAGE_EXTERNAL_STORAGE
        ) != PackageManager.PERMISSION_GRANTED
    }

    // Méthode pour afficher les erreurs
    protected fun showError(error: UserException) {
        val context = context ?: return
        Toast.makeText(context, error.getUserMessage(context), Toast.LENGTH_LONG).show()
    }
}

