<script setup>
import { Badge, Button } from 'frappe-ui'

// Starter screen. The build pipeline replaces it with the screens in the approved spec
// (docs/07); it only proves the front end, session and boot data work on the site.

// The site sets a `user_id` cookie on every response ("Guest" when signed out).
const cookie = (name) =>
  decodeURIComponent(
    document.cookie
      .split('; ')
      .find((c) => c.startsWith(name + '='))
      ?.split('=')[1] || '',
  )
const user = cookie('user_id') || 'Guest'
const signedIn = user !== 'Guest'
const version = window.app_version || 'local'
</script>

<template>
  <div class="min-h-screen bg-surface-gray-1 text-ink-gray-9">
    <header class="flex items-center justify-between border-b bg-surface-white px-5 py-3">
      <h1 class="text-lg font-semibold">Nairobi Fresh Kitchen</h1>
      <div class="flex items-center gap-3">
        <Badge theme="gray" :label="'Release ' + version" />
        <Button v-if="!signedIn" variant="solid" link="/login?redirect-to=/cb">Sign in</Button>
        <Button v-else variant="subtle" link="/app">Open workspace</Button>
      </div>
    </header>
    <main class="mx-auto max-w-2xl px-5 py-12">
      <h2 class="text-2xl font-semibold">Welcome</h2>
      <p class="mt-2 text-base text-ink-gray-6">
        <template v-if="signedIn">Signed in as {{ user }}.</template>
        <template v-else>Sign in to work with your business data.</template>
        The screens designed for your business will appear here.
      </p>
    </main>
  </div>
</template>
