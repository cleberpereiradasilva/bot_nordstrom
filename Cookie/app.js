function getCookie (cname) {
  let name = cname + '='
  let decodedCookie = decodeURIComponent(document.cookie)
  let ca = decodedCookie.split(';')
  for (let i = 0; i < ca.length; i++) {
    let c = ca[i]
    while (c.charAt(0) == ' ') {
      c = c.substring(1)
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length)
    }
  }
  return ''
}

function check_block () {
  const url = window.location.toString()
  if (url.includes('localhost')) {
    console.log('Fechando em 5s')
    setTimeout(() => {
      document.location.href = `http://localhost:8000/close`
    }, 5000)
    return false
  }

  if (url === 'https://siteclosed.nordstrom.com/invitation.html') {
    console.log('Recarrendo em 5s')
    setTimeout(() => {
      document.location.href =
        'https://www.nordstrom.com/brands/la-femme--5309?origin=productBrandLink&page=1'
    }, 5000)
    return false
  }
  return true
}

function check_key () {
  console.log(document.cookie)
  if (check_block()) {
    const dialog = document.querySelector('#dialog-description')
    if (dialog || !getCookie('Bd34bsY56')) {
      location.reload(true)
      return
    }

    const baseUrl = `http://localhost:8000/data`
    fetch(baseUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: '{"cookie": "' + document.cookie + '"}'
    })
      .then(response => response.json())
      .then(() => (document.location.href = `http://localhost:8000/close`))
      .catch(error => console.log('Error:', error))
  }
}
setTimeout(check_key, 2000)
