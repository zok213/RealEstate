"use client";

import React, { useState } from 'react';
import { Settings as SettingsIcon, ArrowLeft, Save, Map, Database, Palette, Bell, Shield, Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function SettingsPage() {
    const router = useRouter();
    const [isSaving, setIsSaving] = useState(false);

    const handleSave = async () => {
        setIsSaving(true);
        // Simulate save
        await new Promise(resolve => setTimeout(resolve, 1000));
        setIsSaving(false);
    };

    return (
        <div className="min-h-screen flex flex-col bg-[#0a140e]">
            {/* Header */}
            <header className="w-full border-b border-[#254632] bg-[#0a140e]">
                <div className="px-6 md:px-10 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <SettingsIcon className="w-8 h-8 text-primary" />
                        <h2 className="text-white text-lg font-bold">Settings</h2>
                    </div>
                    <div className="flex gap-3">
                        <Button
                            variant="outline"
                            className="border-[#254632] text-white hover:bg-[#254632]"
                            onClick={() => router.back()}
                        >
                            <ArrowLeft className="w-4 h-4 mr-2" />
                            Back
                        </Button>
                        <Button
                            className="bg-primary hover:bg-primary/90 text-[#0a140e] font-bold"
                            onClick={handleSave}
                            disabled={isSaving}
                        >
                            <Save className="w-4 h-4 mr-2" />
                            {isSaving ? 'Saving...' : 'Save Changes'}
                        </Button>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <div className="flex-1 flex justify-center py-6 md:py-8 px-4 md:px-10">
                <div className="w-full max-w-[1024px] flex flex-col gap-6">

                    {/* Breadcrumb */}
                    <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-wider">
                        <Link
                            href="/dashboard"
                            className="text-text-muted hover:text-white flex items-center gap-1 transition-colors"
                        >
                            <ArrowLeft className="w-3 h-3" />
                            Dashboard
                        </Link>
                        <span className="text-[#557c66]">/</span>
                        <span className="text-primary">Settings</span>
                    </div>

                    {/* Page Header */}
                    <div className="flex flex-col gap-2">
                        <h1 className="text-white text-3xl md:text-4xl font-bold tracking-tight">
                            Application Settings
                        </h1>
                        <p className="text-text-muted">
                            Configure application preferences and defaults
                        </p>
                    </div>

                    {/* Settings Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                        {/* Design Regulations */}
                        <Card className="bg-[#121d17] border-[#254632]">
                            <CardHeader>
                                <div className="flex items-center gap-3">
                                    <div className="p-2 rounded-lg bg-primary/10 border border-primary/20">
                                        <Shield className="w-5 h-5 text-primary" />
                                    </div>
                                    <div>
                                        <CardTitle className="text-white">Design Regulations</CardTitle>
                                        <CardDescription className="text-text-muted">
                                            Default compliance standards
                                        </CardDescription>
                                    </div>
                                </div>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="flex items-center justify-between p-3 rounded-lg bg-[#0a140e] border border-[#254632]">
                                    <span className="text-white">Active Standard</span>
                                    <span className="text-primary font-medium">IEAT Thailand</span>
                                </div>
                                <div className="flex items-center justify-between p-3 rounded-lg bg-[#0a140e] border border-[#254632]">
                                    <span className="text-white">Min Green Space</span>
                                    <span className="text-text-muted">10%</span>
                                </div>
                                <div className="flex items-center justify-between p-3 rounded-lg bg-[#0a140e] border border-[#254632]">
                                    <span className="text-white">Min Road Width</span>
                                    <span className="text-text-muted">20m</span>
                                </div>
                            </CardContent>
                        </Card>

                        {/* Map Settings */}
                        <Card className="bg-[#121d17] border-[#254632]">
                            <CardHeader>
                                <div className="flex items-center gap-3">
                                    <div className="p-2 rounded-lg bg-primary/10 border border-primary/20">
                                        <Map className="w-5 h-5 text-primary" />
                                    </div>
                                    <div>
                                        <CardTitle className="text-white">Map Display</CardTitle>
                                        <CardDescription className="text-text-muted">
                                            Map visualization preferences
                                        </CardDescription>
                                    </div>
                                </div>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="flex items-center justify-between p-3 rounded-lg bg-[#0a140e] border border-[#254632]">
                                    <span className="text-white">Default View</span>
                                    <span className="text-text-muted">Satellite</span>
                                </div>
                                <div className="flex items-center justify-between p-3 rounded-lg bg-[#0a140e] border border-[#254632]">
                                    <span className="text-white">Show Labels</span>
                                    <span className="text-primary">Enabled</span>
                                </div>
                                <div className="flex items-center justify-between p-3 rounded-lg bg-[#0a140e] border border-[#254632]">
                                    <span className="text-white">Color Scheme</span>
                                    <span className="text-text-muted">Dark</span>
                                </div>
                            </CardContent>
                        </Card>

                        {/* Data Settings */}
                        <Card className="bg-[#121d17] border-[#254632]">
                            <CardHeader>
                                <div className="flex items-center gap-3">
                                    <div className="p-2 rounded-lg bg-primary/10 border border-primary/20">
                                        <Database className="w-5 h-5 text-primary" />
                                    </div>
                                    <div>
                                        <CardTitle className="text-white">Data & Storage</CardTitle>
                                        <CardDescription className="text-text-muted">
                                            Data management options
                                        </CardDescription>
                                    </div>
                                </div>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="flex items-center justify-between p-3 rounded-lg bg-[#0a140e] border border-[#254632]">
                                    <span className="text-white">Auto-save</span>
                                    <span className="text-primary">Enabled</span>
                                </div>
                                <div className="flex items-center justify-between p-3 rounded-lg bg-[#0a140e] border border-[#254632]">
                                    <span className="text-white">Cache Size</span>
                                    <span className="text-text-muted">256 MB</span>
                                </div>
                                <Button
                                    variant="outline"
                                    className="w-full border-[#254632] text-white hover:bg-[#254632]"
                                >
                                    <Download className="w-4 h-4 mr-2" />
                                    Export All Data
                                </Button>
                            </CardContent>
                        </Card>

                        {/* Appearance */}
                        <Card className="bg-[#121d17] border-[#254632]">
                            <CardHeader>
                                <div className="flex items-center gap-3">
                                    <div className="p-2 rounded-lg bg-primary/10 border border-primary/20">
                                        <Palette className="w-5 h-5 text-primary" />
                                    </div>
                                    <div>
                                        <CardTitle className="text-white">Appearance</CardTitle>
                                        <CardDescription className="text-text-muted">
                                            Theme and visual preferences
                                        </CardDescription>
                                    </div>
                                </div>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="flex items-center justify-between p-3 rounded-lg bg-[#0a140e] border border-[#254632]">
                                    <span className="text-white">Theme</span>
                                    <span className="text-primary">Dark</span>
                                </div>
                                <div className="flex items-center justify-between p-3 rounded-lg bg-[#0a140e] border border-[#254632]">
                                    <span className="text-white">Accent Color</span>
                                    <div className="flex items-center gap-2">
                                        <div className="w-4 h-4 rounded-full bg-primary" />
                                        <span className="text-text-muted">Green</span>
                                    </div>
                                </div>
                                <div className="flex items-center justify-between p-3 rounded-lg bg-[#0a140e] border border-[#254632]">
                                    <span className="text-white">Animations</span>
                                    <span className="text-primary">Enabled</span>
                                </div>
                            </CardContent>
                        </Card>
                    </div>

                    {/* API Settings */}
                    <Card className="bg-[#121d17] border-[#254632]">
                        <CardHeader>
                            <CardTitle className="text-white">Backend Connection</CardTitle>
                            <CardDescription className="text-text-muted">
                                API endpoint configuration
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div className="p-4 rounded-lg bg-[#0a140e] border border-[#254632]">
                                    <p className="text-xs text-text-muted uppercase tracking-wider mb-1">Backend URL</p>
                                    <p className="text-white font-mono text-sm">http://localhost:8001</p>
                                </div>
                                <div className="p-4 rounded-lg bg-[#0a140e] border border-[#254632]">
                                    <p className="text-xs text-text-muted uppercase tracking-wider mb-1">Status</p>
                                    <div className="flex items-center gap-2">
                                        <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
                                        <span className="text-primary font-medium">Connected</span>
                                    </div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                </div>
            </div>
        </div>
    );
}
