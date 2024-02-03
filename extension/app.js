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

async function check_key () {
  console.log(document.cookie)
  if (check_block()) {
    const dialog = document.querySelector('#dialog-description')
    if (dialog || !getCookie('Bd34bsY56')) {
      location.reload(true)
      return
    }

    const socket = new WebSocket('ws://localhost:8011')
    while (!socket.readyState) {
      await new Promise(r => setTimeout(r, 1000))
    }
    socket.send(
      JSON.stringify({
        agent: window.navigator.userAgent,
        body: document.body.innerHTML,
        cookie: document.cookie
      })
    )
  }
}
setTimeout(check_key, 2000)
