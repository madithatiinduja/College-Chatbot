(function() {
	const entriesTable = document.getElementById('entriesTable');
	const addBtn = document.getElementById('addBtn');
	const refreshBtn = document.getElementById('refreshBtn');
	const titleInput = document.getElementById('titleInput');
	const keywordsInput = document.getElementById('keywordsInput');
	const responsesInput = document.getElementById('responsesInput');
	const adminTokenInput = document.getElementById('adminToken');
	const uploadPdfBtn = document.getElementById('uploadPdfBtn');
	const pdfTitle = document.getElementById('pdfTitle');
	const pdfKeywords = document.getElementById('pdfKeywords');
	const pdfFile = document.getElementById('pdfFile');

	// Locations elements
	const locName = document.getElementById('locName');
	const locCategory = document.getElementById('locCategory');
	const locMapsQuery = document.getElementById('locMapsQuery');
	const locLat = document.getElementById('locLat');
	const locLng = document.getElementById('locLng');
	const locDesc = document.getElementById('locDesc');
	const addLocationBtn = document.getElementById('addLocationBtn');
	const locationsTable = document.getElementById('locationsTable');

	const getToken = () => adminTokenInput.value.trim();
	const withToken = (url) => {
		const token = getToken();
		if (!token) return url;
		return url + (url.includes('?') ? '&' : '?') + 'admin_token=' + encodeURIComponent(token);
	};

	// Persist token locally for convenience
	(function initTokenPersistence() {
		try {
			const saved = localStorage.getItem('cllgAdminToken');
			if (saved && !adminTokenInput.value) {
				adminTokenInput.value = saved;
			}
			adminTokenInput.addEventListener('input', () => {
				try { localStorage.setItem('cllgAdminToken', adminTokenInput.value.trim()); } catch (_) {}
			});
		} catch (_) {}
	})();

	function handleUnauthorized() {
		alert('Unauthorized: please enter the correct admin token.');
		adminTokenInput.focus();
	}

	async function fetchEntries() {
		const res = await fetch('/api/knowledge');
		if (!res.ok) throw new Error('Failed to load entries');
		const data = await res.json();
		return data.admin_entries || [];
	}

	function renderEntries(entries) {
		entriesTable.innerHTML = '';
		if (!entries.length) {
			const tr = document.createElement('tr');
			const td = document.createElement('td');
			td.colSpan = 4;
			td.textContent = 'No entries yet';
			tr.appendChild(td);
			entriesTable.appendChild(tr);
			return;
		}
		entries.forEach(entry => {
			const tr = document.createElement('tr');
			const tdTitle = document.createElement('td');
			const tdKeywords = document.createElement('td');
			const tdResponses = document.createElement('td');
			const tdActions = document.createElement('td');
			tdTitle.textContent = entry.title || 'Custom';
			tdKeywords.textContent = (entry.keywords || []).join(', ');
			tdResponses.textContent = (entry.responses || []).length + ' response(s)';
			tdActions.className = 'row-actions';
			const editBtn = document.createElement('button');
			const delBtn = document.createElement('button');
			editBtn.className = 'btn secondary';
			delBtn.className = 'btn';
			editBtn.innerHTML = '<i class="fas fa-pen"></i>';
			delBtn.innerHTML = '<i class="fas fa-trash"></i>';
			editBtn.title = 'Edit';
			delBtn.title = 'Delete';
			editBtn.addEventListener('click', () => onEdit(entry));
			delBtn.addEventListener('click', () => onDelete(entry));
			tdActions.appendChild(editBtn);
			tdActions.appendChild(delBtn);
			tr.appendChild(tdTitle);
			tr.appendChild(tdKeywords);
			tr.appendChild(tdResponses);
			tr.appendChild(tdActions);
			entriesTable.appendChild(tr);
		});
	}

	async function fetchLocations() {
		const res = await fetch('/api/locations');
		if (!res.ok) throw new Error('Failed to load locations');
		const data = await res.json();
		return data.locations || [];
	}

	function renderLocations(locations) {
		locationsTable.innerHTML = '';
		if (!locations.length) {
			const tr = document.createElement('tr');
			const td = document.createElement('td');
			td.colSpan = 4;
			td.textContent = 'No locations yet';
			tr.appendChild(td);
			locationsTable.appendChild(tr);
			return;
		}
		locations.forEach(loc => {
			const tr = document.createElement('tr');
			const tdName = document.createElement('td');
			const tdCat = document.createElement('td');
			const tdDest = document.createElement('td');
			const tdActions = document.createElement('td');
			tdActions.className = 'row-actions';
			tdName.textContent = loc.name || 'Unnamed';
			tdCat.textContent = loc.category || '';
			if (loc.latitude != null && loc.longitude != null) {
				tdDest.textContent = `${loc.latitude}, ${loc.longitude}`;
			} else {
				tdDest.textContent = loc.maps_query || '';
			}
			const editBtn = document.createElement('button');
			const delBtn = document.createElement('button');
			editBtn.className = 'btn secondary';
			delBtn.className = 'btn';
			editBtn.innerHTML = '<i class="fas fa-pen"></i>';
			delBtn.innerHTML = '<i class="fas fa-trash"></i>';
			editBtn.title = 'Edit Location';
			delBtn.title = 'Delete Location';
			editBtn.addEventListener('click', () => onEditLocation(loc));
			delBtn.addEventListener('click', () => onDeleteLocation(loc));
			tdActions.appendChild(editBtn);
			tdActions.appendChild(delBtn);
			tr.appendChild(tdName);
			tr.appendChild(tdCat);
			tr.appendChild(tdDest);
			tr.appendChild(tdActions);
			locationsTable.appendChild(tr);
		});
	}

	async function onAddLocation() {
		const name = locName.value.trim();
		const category = locCategory.value.trim();
		const maps_query = locMapsQuery.value.trim();
		const description = locDesc.value.trim();
		const latitude = locLat.value.trim();
		const longitude = locLng.value.trim();
		if (!name) { alert('Please provide a location name.'); return; }
		const body = { name, category, maps_query, description };
		if (latitude) body.latitude = latitude;
		if (longitude) body.longitude = longitude;
		const res = await fetch(withToken('/api/locations'), {
			method: 'POST',
			headers: { 'Content-Type': 'application/json', 'X-Admin-Token': getToken() },
			body: JSON.stringify(body)
		});
		if (!res.ok) {
			const err = await res.json().catch(() => ({}));
			if (res.status === 401) { handleUnauthorized(); return; }
			alert('Failed to add location: ' + (err.error || res.status));
			return;
		}
		locName.value = '';
		locCategory.value = '';
		locMapsQuery.value = '';
		locLat.value = '';
		locLng.value = '';
		locDesc.value = '';
		await load();
	}

	async function onEditLocation(loc) {
		const name = prompt('Name:', loc.name || '')
		if (name === null) return;
		const category = prompt('Category:', loc.category || '')
		if (category === null) return;
		const maps_query = prompt('Maps query (leave blank if using lat/lng):', loc.maps_query || '')
		if (maps_query === null) return;
		const latitude = prompt('Latitude (optional):', (loc.latitude != null ? String(loc.latitude) : ''))
		if (latitude === null) return;
		const longitude = prompt('Longitude (optional):', (loc.longitude != null ? String(loc.longitude) : ''))
		if (longitude === null) return;
		const description = prompt('Description (optional):', loc.description || '')
		if (description === null) return;
		const body = { name: name.trim(), category: category.trim(), maps_query: maps_query.trim(), description: description.trim() };
		if (latitude.trim().length) body.latitude = latitude.trim(); else body.latitude = null;
		if (longitude.trim().length) body.longitude = longitude.trim(); else body.longitude = null;
		const res = await fetch(withToken('/api/locations/' + encodeURIComponent(loc.id)), {
			method: 'PUT',
			headers: { 'Content-Type': 'application/json', 'X-Admin-Token': getToken() },
			body: JSON.stringify(body)
		});
		if (!res.ok) {
			const err = await res.json().catch(() => ({}));
			if (res.status === 401) { handleUnauthorized(); return; }
			alert('Failed to update location: ' + (err.error || res.status));
			return;
		}
		await load();
	}

	async function onDeleteLocation(loc) {
		if (!confirm('Delete this location?')) return;
		const res = await fetch(withToken('/api/locations/' + encodeURIComponent(loc.id)), {
			method: 'DELETE',
			headers: { 'X-Admin-Token': getToken() }
		});
		if (!res.ok) {
			const err = await res.json().catch(() => ({}));
			if (res.status === 401) { handleUnauthorized(); return; }
			alert('Failed to delete location: ' + (err.error || res.status));
			return;
		}
		await load();
	}

	async function onAdd() {
		const title = titleInput.value.trim();
		const keywords = keywordsInput.value.split(',').map(s => s.trim()).filter(Boolean);
		const responses = responsesInput.value.split('\n').map(s => s.trim()).filter(Boolean);
		if (!keywords.length || !responses.length) {
			alert('Please provide at least one keyword and one response.');
			return;
		}
		const res = await fetch(withToken('/api/knowledge'), {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-Admin-Token': getToken()
			},
			body: JSON.stringify({ title, keywords, responses })
		});
		if (!res.ok) {
			const err = await res.json().catch(() => ({}));
			if (res.status === 401) { handleUnauthorized(); return; }
			alert('Failed to add entry: ' + (err.error || res.status));
			return;
		}
		titleInput.value = '';
		keywordsInput.value = '';
		responsesInput.value = '';
		await load();
	}

	async function onEdit(entry) {
		const title = prompt('Title:', entry.title || '');
		if (title === null) return;
		const keywordsStr = prompt('Keywords (comma separated):', (entry.keywords || []).join(', '));
		if (keywordsStr === null) return;
		const responsesStr = prompt('Responses (one per line):', (entry.responses || []).join('\n'));
		if (responsesStr === null) return;
		const body = {
			title: title.trim(),
			keywords: keywordsStr.split(',').map(s => s.trim()).filter(Boolean),
			responses: responsesStr.split('\n').map(s => s.trim()).filter(Boolean)
		};
		const res = await fetch(withToken('/api/knowledge/' + encodeURIComponent(entry.id)), {
			method: 'PUT',
			headers: {
				'Content-Type': 'application/json',
				'X-Admin-Token': getToken()
			},
			body: JSON.stringify(body)
		});
		if (!res.ok) {
			const err = await res.json().catch(() => ({}));
			if (res.status === 401) { handleUnauthorized(); return; }
			alert('Failed to update entry: ' + (err.error || res.status));
			return;
		}
		await load();
	}

	async function onDelete(entry) {
		if (!confirm('Delete this entry?')) return;
		const res = await fetch(withToken('/api/knowledge/' + encodeURIComponent(entry.id)), {
			method: 'DELETE',
			headers: { 'X-Admin-Token': getToken() }
		});
		if (!res.ok) {
			const err = await res.json().catch(() => ({}));
			if (res.status === 401) { handleUnauthorized(); return; }
			alert('Failed to delete entry: ' + (err.error || res.status));
			return;
		}
		await load();
	}

	async function load() {
		try {
			const [entries, locations] = await Promise.all([
				fetchEntries(),
				fetchLocations()
			]);
			renderEntries(entries);
			renderLocations(locations);
		} catch (e) {
			alert('Error loading data');
		}
	}

	addBtn.addEventListener('click', onAdd);
	refreshBtn.addEventListener('click', load);
	document.addEventListener('DOMContentLoaded', load);
	uploadPdfBtn.addEventListener('click', async () => {
		if (!pdfFile.files || !pdfFile.files[0]) { alert('Select a PDF file'); return; }
		const form = new FormData();
		form.append('file', pdfFile.files[0]);
		if (pdfTitle.value.trim()) form.append('title', pdfTitle.value.trim());
		form.append('keywords', pdfKeywords.value.trim());
		const res = await fetch(withToken('/api/knowledge/pdf'), {
			method: 'POST',
			headers: { 'X-Admin-Token': getToken() },
			body: form
		});
		if (!res.ok) {
			const err = await res.json().catch(() => ({}));
			if (res.status === 401) { handleUnauthorized(); return; }
			alert('Failed to upload PDF: ' + (err.error || res.status));
			return;
		}
		pdfTitle.value = '';
		pdfKeywords.value = '';
		pdfFile.value = '';
		await load();
	});

	addLocationBtn.addEventListener('click', onAddLocation);
})();


